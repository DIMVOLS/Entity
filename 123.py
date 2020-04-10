#import spacy
#import pyap
import re
import os
#from spacy.pipeline import EntityRuler
#from spacy.tokenizer import Tokenizer
from spacy.util import compile_prefix_regex, compile_suffix_regex
#from google.cloud import language_v1
#from google.cloud.language_v1 import enums
#from collections import Counter

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/dim/dm_google_vision.json"

# doc_id = 'f2a13f0e994c4d678ff1756ecfc8854d'  # 8.png
# doc_id='e5d38db182e040e4ba9521587cf45395' #10.png
# doc_id='3d15ba6c015942ce90eb24bd31cee758'  #2.png
# doc_id = 'c51f27e3f2494493b5b0f5bdb618b84f' #4.jpg
# doc_id = 'ae620e6ac5a14a95998d2fdd60ce1c76' #20.pdf
# doc_id = 'e9437729482847e5847eaad1146c2359'   #10-k
# doc_id = 'ae37f271db7b498dabb19a0639433cc5'  # 3.png
# doc_id='7c71d589c78d4cc4b7c3c7d195179144'    #5.png
# doc_id='8dfc4a2211e443a4b8bd580389dcac13'    #25.pdf
# doc_id='a8ec515ee3674ab1bd5a73b954d92057'     #16.pdf
# doc_id='3f8ae2df94824b3382305e9474ab40b1'      #10.pdf
# doc_id='8de5cb4dc64a4a46b05cb36e120f7142'    #10-1.pdf
# doc_id='b12dee158d9048fea7e3ad2d3b805d56'    #10-2.pdf
# doc_id='d368b3283064454f82b66b5016a062da'     #10-3.pdf
# doc_id='850c44290f894a09884e81aaf9fe137d'    #10-4.pdf
# doc_id='4685f31b7b6542e29855cbe4498c80c5'    #10-5.pdf
# doc_id='553bfead3a8c4ceea02ec7d6bcfef898'    #10-6.pdf
# doc_id='dfecbc2213e1434c85948b652619b042'    #10-7.pdf
# doc_id='06481c3d1ed34862b4e08b409718c64e'    #10-8.pdf
# doc_id='af1ba410c93c4152bcb00be9660d490c'    #10-9.pdf
# doc_id='af1ba410c93c4152bcb00be9660d490c'     #11.png
# doc_id='9c153c8f4cc24be69903ee8bf767e146'     #12-1.png
# doc_id='e47034cb83c2496b9db701de9edbf248'     #13.png
class EntityComparison:

    def __init__(self, text1=None, text2=None):
        self.text1 = text1
        self.text2 = text2

    def texts_reciever(self):
        self.compare_entities(self.entity_extract(self.text1), self.entity_extract(self.text2))

    @staticmethod
    def custom_tokenizer(nlp):
        infix_re = re.compile(r'''[?;:‘’`“”"'~]''')
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
        time_reg = r'(?: |^)(?:[0-1]?[0-9]|2[0-3])(?:: ?[0-5][0-9]){1,2}\s?(?:[AaPp][Mm])?(?: |$)'
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
                entities_dict[address] = 'LOC'

        elif len(short_address_matches) != 0:
            for address in short_address_matches:
                t = t.replace(str(address), ' ', 1)
                entities_list.append('LOC')
                # print(str(address), " - ADR2")
                entities_dict[address] = 'LOC'

        list1 = {time_reg: 'TIME', zip_reg: 'ZIP', eml_reg: 'EML', currency_reg: 'CURRENCY',
                 tax_reg: 'TAX', phone_reg: 'PHN'}
        for key in list1:
            matches = re.findall(key, t)
            if len(matches) != 0:
                for ent in matches:
                    t = t.replace(ent, '  ', 1)
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
        list2 = {'PHONE_NUMBER': 'PHN', 'DATE': 'DATE', 'PRICE': 'CURRENCY', 'ORGANIZATION': 'ORG',
                 'PERSON': 'PERSON', 'LOCATION': 'LOC'}
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
                                              {"TEXT": {"REGEX": r"(?:(\d{1,3}[ ,]?)+(?:[\.]\d{1,2})?)"}}]},
            {"label": "CURRENCY", "pattern": [{'LEMMA': {'IN': ['pay', 'earn', 'win',
                                                                'refund', 'spend',
                                                                'save', 'invest',
                                                                'send', 'return', 'own', 'borrow', 'make',
                                                                'inherit',
                                                                'find', 'waste', 'lose', 'lend']}},
                                              {"TEXT": {"REGEX": r'\W'}, 'OP': '?'},
                                              {"TEXT": {"REGEX": r"(?:(\d{1,3}[ ,]?)+(?:[\.]\d{1,2})?)"}}]}

        ]
        ruler.add_patterns(patterns)
        # Priority of ruler
        nlp.add_pipe(ruler, before="ner")
        doc = nlp(t)
        gen = (ents for ents in doc.ents if ents.label_ not in ['DATE'])

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
            # print(entity.text, "-", entity.label_)
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

tex2 = "European authorities in 20:30 fined Google a record $5.1 billion on Wednesday for abusing its power in the mobile phone market and ordered the company to alter its practices"
tex1 = "qw21"
# Comparing 2 texts
texts = EntityComparison(tex1, tex2)
#texts.texts_reciever()

# Only entity extracting

texts.entity_extract(tex2)
