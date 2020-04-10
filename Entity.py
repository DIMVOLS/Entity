import spacy
import pyap
import re
import os
from spacy.pipeline import EntityRuler
from spacy.tokenizer import Tokenizer
from spacy.util import compile_prefix_regex, compile_suffix_regex
from google.cloud import language_v1
from google.cloud.language_v1 import enums
from collections import Counter
from collections import defaultdict

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/dim/dm_google_vision.json"


class EntityComparison:

    def __init__(self, text1=None, text2=None):
        self.text1 = text1
        self.text2 = text2

    def texts_reciever(self):
        self.compare_entities(self.entity_extract(self.text1), self.entity_extract(self.text2))

    @staticmethod
    def custom_tokenizer(nlp):
        infix_re = re.compile(r'''[?;‘’`“”"'~]''')
        prefix_re = compile_prefix_regex(nlp.Defaults.prefixes)
        suffix_re = compile_suffix_regex(nlp.Defaults.suffixes)

        return Tokenizer(nlp.vocab, prefix_search=prefix_re.search,
                         suffix_search=suffix_re.search,
                         infix_finditer=infix_re.finditer)

    def entity_extract(self, text):
        t = text
        persons = []
        organizations = []
        entities_list = []
        entities_dict = {}
        time_reg = r'(?: |^)((?:[0-1]?[0-9]|2[0-3])(?:: ?[0-5][0-9]){1,2}\s?(?:[AaPp][Mm])?)(?: |$)'
        tax_reg = r'\b(?![01][789]|2[89]|[46]9|7[089]|89|9[67])\d\d-\d{7}\b'
        zip_reg = r'\W\d{5}(?:[-\s]\d{4})\W'

        short_address = re.compile(r'\W(\d{1,4}[a-zA-Z .]{2,10}[\w\s]{2,20} (?:street|st|avenue|ave|road|rd'
                                   r'|highway|hwy|square|sq|trail|trl|drive|dr|court|ct|park|parkway|pkwy|circle'
                                   r'|cir|boulevard|blvd|way|place|route|avn|lane|av))\W', re.IGNORECASE)

        phone_reg = (r'(?:(?:\+?\d{1,3}?[-.* ]?){0,2}(?:\+?\(?\d{3}\)? ?[-.\/* ]?)? ?'
                     r'\d{3}[-.* ]\d{3,5}(?![\d-]))')

        currency_reg = (r'(?:(?:[\$M¢£¥元圓€₹]\s*(?:(?:\d+[ ,])+)?\d+(?:[.,]?\d\d?)?)|'
                        r'(?:(?:(?:\d+[ ,])+)?\d+(?:[.,]?\d{1,2}?)?\s*[\$M¢£¥元圓€₹])|'
                        r'(?:(?:\d{1,3}[ ,]?)+[\.]\d{1,2})(?:\s|$))')

        eml_reg = r'([-\w.]+ ?@ ?(?:[A-z0-9][-A-z0-9]+\.)+ ?[A-z]{2,4})'

        long_address_matches = pyap.parse(t, country='US')
        short_address_matches = short_address.findall(t)
        if len(long_address_matches) != 0:
            for address in long_address_matches:
                t = re.sub(str(address), ' ', t)
                entities_list.append('LOC')
                # print(str(address), " - ADR1")
                entities_dict[address] = 'LOC2'

        elif len(short_address_matches) != 0:
            for address in short_address_matches:
                t = t.replace(str(address), ' ', 1)
                entities_list.append('LOC3')
                # print(str(address), " - ADR2")
                entities_dict[address] = 'LOC'

        list1 = {time_reg: 'TIME', zip_reg: 'ZIP', eml_reg: 'EML', currency_reg: 'CURRENCY',
                 tax_reg: 'TAX', phone_reg: 'PHN'}
        for key in list1:
            matches = re.findall(key, t)
            if len(matches) != 0:
                for ent in matches:
                #    t = t.replace(ent, '  ', 1)
                    entities_list.append(list1[key])
                    entities_dict[ent] = list1[key]

        client = language_v1.LanguageServiceClient()
        type_ = enums.Document.Type.PLAIN_TEXT

        language = "en"
        document = {"content": t, "type": type_, "language": language}

        # Available values: NONE, UTF8, UTF16, UTF32
        encoding_type = enums.EncodingType.UTF8
        response = client.analyze_entities(document, encoding_type=encoding_type)

        # Google extraction
        list2 = {'PHONE_NUMBER': 'PHN1', 'DATE': 'DATE', 'PRICE': 'CURRENCY', 'ORGANIZATION': 'ORG',
                 'PERSON': 'PERSON',  'ADDRESS':'ADDRESS1'}
        for key in list2:
            for entity in response.entities:
                if enums.Entity.Type(entity.type).name == key:
                    if key == 'ORGANIZATION':
                        organizations.append(entity.name)
                        continue
                    entities_list.append(list2[key])
                    if key == 'PERSON':
                        persons.append(entity.name)
                        continue
                    entities_dict[entity.name] = list2[key]
                    t = t.replace(entity.name, '  ', 1)
                   # print(entity.name,enums.Entity.Type(entity.type).name)
                   # print(t)

        nlp = spacy.load("en_core_web_sm")
        # Changing default tokenizer to created
        nlp.tokenizer = self.custom_tokenizer(nlp)
        ruler = EntityRuler(nlp, overwrite_ents=True)

        patterns = [
            {"label": "TAX", "pattern": [{"TEXT": {"REGEX": r"^(?![01][789]|2[89]|[46]9|7[089]|89|9[67])"
                                                            r"\d{2}-\d{7}$"}}]},
            {"label": "URL",
             "pattern": [{"TEXT": {"REGEX": r"^([a-zA-Z0-9]([a-zA-Z0-9]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,6}$"}}]},
            {"label": "DATE", "pattern": [{"TEXT": {
                "REGEX": r"^(19|20)\d{2}-((0[1-9]|1[012])-(0[1-9]|[12]\d)|(0[13-9]|1[012])-30|"
                         r"(0[13578]|1[02])-31)$"}}]},
            {"label": "DATE", "pattern": [
                {"TEXT": {"REGEX": r"^(0?[1-9]|[12][0-9]|3[01])[- /.](0?[1-9]|[12][0-9]|3[01])[- /.](19|20)\d\d$"}}]},
            {"label": "PHONE",
             "pattern": [{'LOWER': {'IN': ['phone', 'telephone', 'cell-phone', 'cellphone', 'cellular',
                                           'cell', 'fax']}},
                         {"TEXT": {"REGEX": r'\W'}, 'OP': '?'},
                         {"TEXT": {"REGEX": r"(?:\+?[\/\(\)-.*\d]{3,18})"}},
                         {"TEXT": {"REGEX": r"(?:\+?[\/\(\)-.\* ]*\d{2,3}[\/\(\)-.\* ]*)"}, 'OP': '*'}]},
            {"label": "LOC", "pattern": [{'LOWER': {'IN': ['address', 'adr']}},
                                         {"TEXT": {"REGEX": r'\W'}, 'OP': '?'},
                                         {"TEXT": {"REGEX": r"([\w.]{1,15})"}, 'OP': '+'}]},
            {"label": "CURRENCY", "pattern": [{'LOWER': {'IN': ['total', 'amount', 'balance', 'USD', 'due',
                                                                'summary', 'worth', 'dollars', 'cost',
                                                                'discount',
                                                                'payment', 'val', 'price', ]}},
                                              {"TEXT": {"REGEX": r'\W'}, 'OP': '?'},
                                              {"TEXT": {"REGEX": r"(?:(\d{1,3}[ ,]?)+(?:[\.]\d{1,2})?)"}},
                                              {'LOWER': {'IN': ['usd','euro','jpy','gbp','chf','cad','zar']},'OP': '?'}]},
            {"label": "CURRENCY", "pattern": [{'LEMMA': {'IN': ['pay', 'earn', 'win',
                                                                'refund', 'spend',
                                                                'save', 'invest',
                                                                'send', 'return', 'own', 'borrow', 'make',
                                                                'inherit',
                                                                'find', 'waste', 'lose', 'lend']}},
                                              {"TEXT": {"REGEX": r'\W'}, 'OP': '?'},
                                              {"TEXT": {"REGEX": r"(?:(\d{1,3}[ ,]?)+(?:[\.]\d{1,2})?)"}},
                                              {'LOWER': {'IN': ['usd','euro','jpy','gbp','chf','cad','zar']},'OP': '?'}
                                              ]}

        ]
        ruler.add_patterns(patterns)
        # Priority of ruler
        nlp.add_pipe(ruler, before="ner")
        doc = nlp(t)



        gen = (ents for ents in doc.ents if ents.label_ not in ['DATE'])

        beams = nlp.entity.beam_parse([doc], beam_width=16, beam_density=0.0001)

        entity_scores = defaultdict(float)

        for beam in beams:
            for score, ents in nlp.entity.moves.get_beam_parses(beam):
                for start, end, label in ents:
                    entity_scores[(start, end, label)] += score


        for key in entity_scores:
            start, end, label = key
            print((f'words : {doc[start: end]} \n'
                   f' type: {label}\n '
                   f'with a confidence score = {entity_scores[key]}'))



        print("Persons- ",persons)
        print("Orgs- ",organizations)
        for entity in gen:
            if entity.label_ == 'ORG':
                if any([True for x in [organizations, persons] if entity.text in str(x)]):
                    entities_dict[entity.text] = 'ORG'
                    continue
                else:
                    for words in organizations:
                        if words in entity.text:
                            entities_dict[entity.text] = 'ORG'
                    continue
            elif entity.text in str(persons) or [True for x in persons if x in entity.text]:
                entities_dict[entity.text] = 'PERSON'
                continue

            entities_list.append(entity.label_)
            entities_dict[entity.text] = entity.label_
            print(entity.text, "-", entity.label_)
        print(entities_dict)
        return entities_dict

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

tex2  = """(location,
  'and 4 facility Blackberry Professional Manassas, and VA Data Recovery 20854 Drive, Suite 143 Gaithersburg, and MD FBI 20879 Facility 9520 Reach Blackberry Road Potomac, MD'),
 (currency,
  '150.00 262.50 150.00 150.00 $820.00 1.6 150.00 1.75 240.00 $0.00 150.00 0.50 150.00 17.50 $820.00'),
 (phone, '301-947-7475'),
 (organization,
  'FOLSON Forensic Forensics FBI DIGITAL Expert FORENSICS Forensic Digital Forensic'),
 (date, '05/06/10 06/04/10 04/29/10 06/03/10 04/29/10 05/05/10'),
 (person,
  'Forensics Cell FORENSICS Phone Forensic cell phone. Cell Phone Cell phone Forensic Cell Mark Phone Cell Carroll Forensic Phone cell phone'),
 (number, '21 35')]
"""
tex1 = """
Nokia John Glenn JPMorgan Chase Buzz Aldrin Ping An Insurance Group Wells Fargo Omar Bradley Bank of America Charlie Bury Robert Crippen Francis S. Currey Jimmy Doolittle
Dwight China Construction Bank D. Eisenhower  China Construction Bank John R. Fox Apple Ulysses S. Grant ICBC
"""
# Comparing 2 texts
texts = EntityComparison(tex1, tex2)
#texts.texts_reciever()

# Only entity extracting

texts.entity_extract(tex2)
