import re
import os
import sys
import pyap
import spacy
import boto3
from enum import Enum
from collections import defaultdict
from google.cloud import language_v1
from google.cloud.language_v1 import enums
from spacy.pipeline import EntityRuler
from spacy.tokenizer import Tokenizer
from spacy.util import compile_prefix_regex, compile_suffix_regex

import dxtract.entity.utils as utils
from dxtract.base import DxObject
from configs.config import ee_settings as ent_engines

working_dir = os.path.abspath(os.getcwd())
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(
    working_dir, "configs/auth_config_google_vision.json")
# os.environ["AWS_SHARED_CREDENTIALS_FILE"] = os.path.join(
#     working_dir, "configs/auth_config_aws.json")
spacy_nlp = None


class EntityClass(Enum):
    """Entity Class"""

    ENTITY_PERSON = 'person'
    ENTITY_ORGANIZATION = 'organization'
    ENTITY_CURRENCY = 'currency'
    ENTITY_EMAIL = 'email'
    ENTITY_PHONE_NUMBER = 'phone_number'
    ENTITY_LOCATION = 'location'
    ENTITY_NUMBER = 'number'
    ENTITY_PERCENT = 'percent'
    ENTITY_DATE = 'date'
    ENTITY_TIME = 'time'
    ENTITY_TAX_ID = 'tax_id'
    ENTITY_ZIP = 'zip'
    ENTITY_TEXT = 'text'


class EntityEngine:
    """Base class for Entity Engine"""

    def __init__(self):
        self._name = type(self).__name__
        self.entities = []

    name = property(lambda self: self._name)

    @classmethod
    def from_config(cls, config):
        ee = cls()
        ee._name = config.get('name')

    def extract_entities(self, text):
        pass


class RegexEngine(EntityEngine):
    CODEC = {
        'LOCATION': EntityClass.ENTITY_LOCATION,
        'DATE': EntityClass.ENTITY_DATE,
        'TIME': EntityClass.ENTITY_TIME,
        'CURRENCY': EntityClass.ENTITY_CURRENCY,
        'PHONE_NUMBER': EntityClass.ENTITY_PHONE_NUMBER,
        'ZIP': EntityClass.ENTITY_ZIP,
        'TAX_ID': EntityClass.ENTITY_TAX_ID,
        'EMAIL': EntityClass.ENTITY_EMAIL
    }

    def __init__(self):
        super().__init__()

    def extract_entities(self, text):

        regexs = {
            'TIME': utils.TIME_REGEX,
            'DATE': utils.DATE_REGEX,
            'ZIP': utils.ZIP_REGEX,
            'EMAIL': utils.EMAIL_REGEX,
            'CURRENCY': utils.CURRENCY_REGEX,
            'TAX_ID': utils.TAX_REGEX,
            'PHONE_NUMBER': utils.PHONE_NUMBER_REGEX,
        }

        long_address_matches = pyap.parse(text, country='US')
        short_address_matches = re.findall(utils.SHORT_ADDRESS_REGEX, text)
        if len(long_address_matches) != 0:
            for address in long_address_matches:
                text = text.replace(str(address), ' ', 1)
                self.entities.append({
                    'text': str(address),
                    'type': self.CODEC['LOCATION'],
                    'score': 1
                })

        elif len(short_address_matches) != 0:
            for address in short_address_matches:
                text = text.replace(str(address), ' ', 1)
                self.entities.append({
                    'text': str(address),
                    'type': self.CODEC['LOCATION'],
                    'score': 1
                })

        for key in regexs:
            matches = re.findall(regexs[key], text)
            if len(matches) != 0:
                for ent in matches:
                    ent = ent[0] if isinstance(ent, tuple) else ent
                    text = text.replace(ent, '  ', 1)
                    self.entities.append({
                        'text': str(ent),
                        'type': self.CODEC[key],
                    })

        return self.entities


class AwsEngine(EntityEngine):
    """Amazon Entity Engine"""

    CODEC = {
        'PERSON': EntityClass.ENTITY_PERSON,
        'LOCATION': EntityClass.ENTITY_LOCATION,
        'ORGANIZATION': EntityClass.ENTITY_ORGANIZATION,
        'DATE': EntityClass.ENTITY_DATE,
        # Quantified amount, such as currency, percentages, numbers, bytes..
        'QUANTITY': EntityClass.ENTITY_NUMBER
    }

    def __init__(self):
        super().__init__()
        self.comprehend = None

    def extract_entities(self, text):
        language = "en"
        self.entities = []
        if self.comprehend is not None:
            aws_response = self.comprehend.detect_entities(Text=text,
                                                           LanguageCode=language)

            for entity in aws_response['Entities']:
                if entity['Type'] in self.CODEC:
                    self.entities.append({
                        'text': entity['Text'],
                        'type': self.CODEC[entity['Type']],
                        'score': entity['Score'],
                    })

        return self.entities


class GoogleEngine(EntityEngine):
    """Google NLP Entity Engine"""

    CODEC = {
        'PERSON': EntityClass.ENTITY_PERSON,
        'LOCATION': EntityClass.ENTITY_LOCATION,
        'ORGANIZATION': EntityClass.ENTITY_ORGANIZATION,
        'DATE': EntityClass.ENTITY_DATE,
        'PHONE_NUMBER': EntityClass.ENTITY_PHONE_NUMBER,
        'ADDRESS': EntityClass.ENTITY_LOCATION,
        'PRICE': EntityClass.ENTITY_CURRENCY,
        'NUMBER': EntityClass.ENTITY_NUMBER
    }

    def __init__(self):
        super().__init__()

    def extract_entities(self, text):
        client = language_v1.LanguageServiceClient()
        type_ = enums.Document.Type.PLAIN_TEXT

        language = "en"

        document = {
            "content": text,
            "type": type_,
            "language": language
        }

        # Available values: NONE, UTF8, UTF16, UTF32
        encoding_type = enums.EncodingType.UTF8
        google_response = client.analyze_entities(document, encoding_type)

        # Google extraction
        for entity in google_response.entities:
            if enums.Entity.Type(entity.type).name in self.CODEC:
                self.entities.append({
                    'text': entity.name,
                    'type': self.CODEC[enums.Entity.Type(entity.type).name],
                })
                # self.text = self.text.replace(entity.name, '  ', 1)

        return self.entities


class SpacyEngine(EntityEngine):
    """Spacy Entity Engine"""

    CODEC = {
        'PERSON': EntityClass.ENTITY_PERSON,
        # geo-politcal entities(countries, cities, states.)
        'GPE': EntityClass.ENTITY_LOCATION,
        # Non-GPE locations, mountain ranges, bodies of water.
        'LOC': EntityClass.ENTITY_LOCATION,
        'ORG': EntityClass.ENTITY_ORGANIZATION,
        'DATE': EntityClass.ENTITY_DATE,
        'TIME': EntityClass.ENTITY_TIME,
        'MONEY': EntityClass.ENTITY_CURRENCY,
        'NUMBER': EntityClass.ENTITY_NUMBER,
        'QUANTITY': EntityClass.ENTITY_NUMBER,
        'PERCENT': EntityClass.ENTITY_NUMBER,
        'CARDINAL': EntityClass.ENTITY_NUMBER,
        'ORDINAL': EntityClass.ENTITY_NUMBER
    }

    def __init__(self):
        super().__init__()
        self.nlp = spacy_nlp
        if spacy_nlp is None:
            self.nlp = spacy.load(ent_engines['spacy']['models']['small'])

    @staticmethod
    def custom_tokenizer(nlp):
        infix_re = re.compile(r'''[?;‘’`“”"'~]''')
        prefix_re = compile_prefix_regex(nlp.Defaults.prefixes)
        suffix_re = compile_suffix_regex(nlp.Defaults.suffixes)
        tokenizer = Tokenizer(nlp.vocab)
        tokenizer.prefix_search = prefix_re.search
        tokenizer.suffix_search = suffix_re.search
        tokenizer.infix_finditer = infix_re.finditer
        tokenizer.token_match = None
        return tokenizer

    def extract_entities(self, text):
        spacy_scores = {}

        nlp = spacy.load("en_core_web_sm")

        # Changing default tokenizer to created
        nlp.tokenizer = self.custom_tokenizer(nlp)
        ruler = EntityRuler(nlp, overwrite_ents=True)
        ruler.add_patterns(utils.SPACY_PATTERNS)
        # Priority of ruler
        nlp.add_pipe(ruler, before="ner")
        doc = nlp(text)
        entity_list = (ents for ents in doc.ents if ents.label_ != 'DATE')
        # Spacy scores
        beams = nlp.entity.beam_parse([doc], beam_width=16, beam_density=0.001)
        entity_scores = defaultdict(float)

        for beam in beams:
            for score, en_list in nlp.entity.moves.get_beam_parses(beam):
                for start, end, label in en_list:
                    entity_scores[(start, end, label)] += score

        for key in entity_scores:
            start, end, label = key
            spacy_scores.update({(str(doc[start: end]), label):
                                entity_scores[key]})

        ents = []
        
        for entity in entity_list:
            if entity.label_ in self.CODEC:
                ents.append({
                    'text': entity.text,
                    'type': self.CODEC[entity.label_],
                    #'score': spacy_scores[(entity.text, entity.label_)]
                })

        for i in ents:
            if i not in self.entities:
                self.entities.append(i)
        return self.entities


class Entity(DxObject):

    def __init__(self, words, entity_class):
        super().__init__()
        self._entity_class = entity_class
        if words:
            self._words = words
            self.append_words()

    words = property(lambda self: self._words)
    entity_class = property(lambda self: self._entity_class)

    @classmethod
    def from_model(cls, model, page):
        entity = cls(words=[page.words[w['id']] for w in model['words']],
                     entity_class=EntityClass(model['entity_type']))
        return entity

    def get_model(self):
        model = super().get_model()
        model.update({
            'words': [w.model for w in self.words],
            'entityClass': self._entity_class.value,
        })
        return model

    @property
    def text(self):
        return ' '.join([w.value for w in self.words])

    def __repr__(self):
        return self.text + '  :  ' + self.entity_class.value

    def append_words(self):
        for word in self._words:
            word._entity = self


class EntityExtractor(object):

    def __init__(self, page, entity_engines):
        """

        Args:
            page: DocumentPage
            entity_engines: [str]
                A list of entity engine classes.
        """
        self.page = page
        self.entity_engines = entity_engines
        self.entities = {}

    def get_entities_list(self, entities_dict):
        entity_list = []
        doc_words = [word for word in self.page.words]
        priority_list = {ent_engines[item]['priority']:
                         ent_engines[item]['name']
                         for item in ent_engines}
        for priority, engine in priority_list.items():
            if engine not in self.entity_engines:
                continue
            for item in entities_dict[engine]:

                possible_words = self.page.get_words_by_value(
                    item['text'].split()[0], doc_words)
                for word_p in possible_words:
                    words = [word_p]

                    while word_p.line.block.get_next_block_word(words[-1]):
                        next_word = \
                            word_p.line.block.get_next_block_word(words[-1])
                        if next_word.value in item['text']:
                            words.append(next_word)
                        else:
                            break
                    if len(words) == len(item['text'].split()):
                        entity_list.append(Entity(words, item['type']))
                        for word in words:
                            if word in doc_words:
                                doc_words.remove(word)
        print(entity_list)
        return entity_list

    def extract(self, text=None):
        """Extracts entities from a list of words.

        Returns:
            List of entities objects

        """
        if text is None:
            text = []
            for block in self.page.blocks:
                block_text = ''
                for line in block.lines:
                    block_text += \
                        ' '.join([word.value for word in line.words]) + ' '
                text.append(block_text)
            separator = ' noise ' * 3 + '. '
            text = separator.join(text)


        for ee_class_name in self.entity_engines:
            engine_class = ent_engines[ee_class_name]['class']
            ee = getattr(sys.modules['dxtract.entity.entities'], engine_class)()
            self.entities[ee_class_name] = ee.extract_entities(text)

        return self.get_entities_list(self.entities)
