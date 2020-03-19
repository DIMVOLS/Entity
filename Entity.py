import spacy
import pyap
import spacy.pipeline
import re
from spacy.pipeline import EntityRuler
from spacy.tokenizer import Tokenizer
from spacy.util import compile_prefix_regex, compile_suffix_regex
from google.cloud import language_v1
from google.cloud.language_v1 import enums
import os
from collections import Counter

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/dim/dm_google_vision.json"


class EntityComparison:
    def __init__(self, text1=None, text2=None):
        self.text1 = text1
        self.text2 = text2

    def texts_reciever(self):
        self.compare_entities(self.entity_extract(self.text1), self.entity_extract(self.text2))

    @staticmethod
    def custom_tokenizer(nlp):
        infix_re = re.compile(r'''[?\;\‘\’\`\“\”\"\'~]''')
        prefix_re = compile_prefix_regex(nlp.Defaults.prefixes)
        suffix_re = compile_suffix_regex(nlp.Defaults.suffixes)

        return Tokenizer(nlp.vocab, prefix_search=prefix_re.search,
                         suffix_search=suffix_re.search,
                         infix_finditer=infix_re.finditer,
                         token_match=None)

    def entity_extract(self, text):
        t = text
        print(t)
        entities_list = []
        # Loop through entitites returned from the API

        tax_regex = r'\b(?![01][789]|2[89]|[46]9|7[089]|89|9[67])\d\d-\d{7}\b'
        tax_matches = re.findall(tax_regex, t)

        short_address = re.compile(r'(?: |^)(\d{1,4}[a-zA-Z .]{2,10}[\w\s]{2,20} (?:street|st|avenue|ave|road|rd|'
                                   r'highway|hwy|square|sq|trail|trl|drive|dr|court|ct|park|parkway|pkwy|circle|cir|'
                                   r'boulevard|blvd|way|place|route|avn|lane|av))(?:|$)', re.IGNORECASE)

        phone_reg = (r'(?:(?:\d{2}-)?(?:\+?\d{1,3}?[-.* ]?){0,2}(?:\+?\(?\d{3}\)? ?[-.\/* ]?)? ?\d{3}[-.*]?'
                     r'\d{4,5}(?![\d-]))')
        currency_reg = (r'(?:\s|^)(?:(?:[\$M¢£¥元圓€₹]\s*(?:(?:\d+[ ,])+)?\d+(?:[.,]?\d\d?)?)|'
                        r'(?:(?:(?:\d+[ ,])+)?\d+(?:[.,]?\d{1,2}?)?\s*[\$M¢£¥元圓€₹])|'
                        r'(?:(?:\d{1,3}[ ,]?)+[\.]\d{1,2}))(?:\s|$)')
        currency_matches = re.findall(currency_reg, t)

        if len(currency_matches) != 0:
            for currency in currency_matches:
                t = t.replace(currency, ' ', 1)
                entities_list.append('MONEY')
                # print(currency, " - MONEY")

        if len(tax_matches) != 0:
            for tax in tax_matches:
                t = t.replace(tax, ' ', 1)
                entities_list.append('TAX')
                # print(tax, " - TAX")

        phone_matches = re.findall(phone_reg, t)
        if len(phone_matches) != 0:
            for phone in phone_matches:
                t = t.replace(phone, ' ', 1)
                entities_list.append('PHN')
                # print(str(phone), " - PHN")

        long_address_matches = pyap.parse(t, country='US')
        short_address_matches = short_address.findall(t)
        if len(long_address_matches) != 0:
            for address in long_address_matches:
                t = re.sub(str(address), ' ', t)
                entities_list.append('LOC')
                # print(str(address), " - ADR1")

        elif len(short_address_matches) != 0:
            for address in short_address_matches:
                t = t.replace(str(address), ' ', 1)
                entities_list.append('LOC')
                # print(str(address), " - ADR2")

        client = language_v1.LanguageServiceClient()

        type_ = enums.Document.Type.PLAIN_TEXT
        language = "en"
        document = {"content": t, "type": type_, "language": language}
        encoding_type = enums.EncodingType.UTF8
        response = client.analyze_entities(document, encoding_type=encoding_type)
        persons = []
        organizations = []
        # Google extraction
        for entity in response.entities:
            if enums.Entity.Type(entity.type).name == 'PHONE_NUMBER':
                t = t.replace(entity.name, ' ', 1)
                entities_list.append('PHN')
            if enums.Entity.Type(entity.type).name == 'DATE':
                t = t.replace(entity.name, ' ', 1)
                entities_list.append('DATE')
                # print(entity.name, "DATE1")
            elif enums.Entity.Type(entity.type).name == 'PRICE':
                t = t.replace(entity.name, ' ', 1)
                entities_list.append('CURRENCY')
                # print(entity.name, "MONEY1")
            elif enums.Entity.Type(entity.type).name == 'PERSON':
                entities_list.append('PERSON')
                persons.append(entity.name)
                # print(entity.name,"PERSON")
            elif enums.Entity.Type(entity.type).name == 'ORGANIZATION':
                if entity.salience > 0.1 and entity.name in t:
                    organizations.append(entity.name)
                    entities_list.append('ORG')
                    t = t.replace(entity.name, ' ', 1)
                    # print(entity.name, "ORG1")
        # print(t)
        nlp = spacy.load("en_core_web_sm")
        # Changing default tokenizer to created
        nlp.tokenizer = self.custom_tokenizer(nlp)
        ruler = EntityRuler(nlp, overwrite_ents=True)

        patterns = [
            {"label": "TAX", "pattern": [{"TEXT": {"REGEX": "^(?![01][789]|2[89]|[46]9|7[089]|89|9[67])"
                                                            "\d{2}-\d{7}$"}}]},
            {"label": "EML", "pattern": [{"TEXT": {"REGEX": "^[-\w.]+@([A-z0-9][-A-z0-9]+\.)+[A-z]{2,4}$"}}]},
            {"label": "URL",
             "pattern": [{"TEXT": {"REGEX": "^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,6}&"}}]},
            {"label": "DATE", "pattern": [{"TEXT": {
                "REGEX": "^(19|20)\d\d-((0[1-9]|1[012])-(0[1-9]|[12]\d)|(0[13-9]|1[012])-30|(0[13578]|1[02])-31)$"}}]},
            {"label": "DATE", "pattern": [
                {"TEXT": {"REGEX": "^(0?[1-9]|[12][0-9]|3[01])[- /.](0?[1-9]|[12][0-9]|3[01])[- /.](19|20)\d\d$"}}]},
            {"label": "ZIP", "pattern": [{"TEXT": {"REGEX": "^\d{5}(?:[-\s]\d{4})?$"}}]},
            {"label": "TIME", "pattern": [{"TEXT": {"REGEX": "^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$"}}]},
            {"label": "CURRENCY", "pattern": [{'LOWER': {'IN': ['total', 'amount', 'subtotal', 'balance', 'USD', 'due',
                                                             'summary', 'worth', 'dollars', 'cost', 'discount',
                                                             'paid', 'val', 'price']}},
                                           {"TEXT": {"REGEX": '\W'}, 'OP': '?'},
                                           {"TEXT": {"REGEX": "(?:(\d{1,3}[ ,]?)+(?:[\.]\d{1,2})?)"}}]},
            {"label": "CURRENCY", "pattern": [{'LEMMA': {'IN': ['pay', 'earn', 'win', 'refund', 'spend', 'save', 'invest',
                                                             'send', 'return', 'own', 'borrow', 'make', 'inherit',
                                                             'find', 'waste', 'lose', 'lend']}},
                                           {"TEXT": {"REGEX": '\W'}, 'OP': '?'},
                                           {"TEXT": {"REGEX": "(?:(\d{1,3}[ ,]?)+(?:[\.]\d{1,2})?)"}}]}
        ]
        ruler.add_patterns(patterns)
        # Priority of ruler
        nlp.add_pipe(ruler, before="ner")
        doc = nlp(t)
        for entity in doc.ents:
            if entity.label_ == 'ORG' and entity.text in persons:
                entities_list.remove('PERSON')
            if entity.label_ == 'PERSON' and entity.text in persons:
                continue
            entities_list.append(entity.label_)
            # print(entity.text, "-", entity.label_)
        print(sorted(entities_list))

        return entities_list

    @staticmethod
    def compare_entities(entities_list, entities_list2):
        longest_entity_list = max(len(entities_list), len(entities_list2))

        matched_entities = list((Counter(entities_list) & Counter(entities_list2)).elements())
        differences_1 = list((Counter(entities_list) - Counter(matched_entities)).elements())
        differences_2 = list((Counter(entities_list2) - Counter(matched_entities)).elements())

        max_differences = max(len(differences_1), len(differences_2))

        final_score = 1 - (max_differences / longest_entity_list)

        # Similarity coefficient
        print(final_score)

        if final_score < 0.65:
            print('NO')
        else:
            print('YES')


# Text examples
#tex1 = (' Dan Fink LLC.'
#        '     5 643$'
#        ' 2342 East Broadway'
#        ' phone:78787132123 TAX # 86-0813450')

#tex2 = ('Alex  so today'
#        ' Romashka Ltd.'
#        ' 2481 Es 22nd St TUCSON, AZ 34343'
#        ' March 3'
#        ' Subtotal: 2324')

# Comparing 2 texts
#texts = EntityComparison(tex1, tex2)
#texts.texts_reciever()

# Only entity extracting
#texts.entity_extract(tex2)
