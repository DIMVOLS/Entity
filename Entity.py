import spacy
import pyap
import spacy.pipeline
import re
from spacy.pipeline import EntityRuler
from collections import Counter
from spacy.tokenizer import Tokenizer
from spacy.util import compile_prefix_regex, compile_infix_regex, compile_suffix_regex
from spacy import displacy

class EntityComparison:
    def __init__(self, text1, text2=None):
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
        entities_list = []

        tax_regex = (r'\b(?![01][789]|2[89]|[46]9|7[089]|89|9[67])\d\d-\d{7}\b')
        tax_matches = re.findall(tax_regex, t)

        short_address = re.compile(r'(?:\s|^)(\d{1,4}[a-zA-Z\ \.]{2,10}[\w\s]{1,20}(?:street|st|avenue|ave|road|'
                                   r'rd|highway|hwy|square|sq|trail|trl|drive|dr|court|ct|park|parkway|pkwy|circle|'
                                   r'cir|boulevard|blvd|way|place|route|avn|lane|av)(?:\s|$))', re.IGNORECASE)

        phone_reg = (r'(?:(?: |^)|[:#])(?:(?:\+?\d{1,3}?[-.* ]?){0,2}(?:\+?\(?\d{3}\)? ?[-.\/* ]?)? ?\d{3}[-.* ]?'
                     r'\d{4,5}(?![\d-]))(?:[ .,]|$)')
        currency_reg = (r'(?:\s|^)(?:(?:[\$M¢£¥元圓€₹]\s*(?:(?:\d+[ ,])+)?\d+(?:[.,]?\d\d?)?)|'
                        r'(?:(?:(?:\d+[ ,])+)?\d+(?:[.,]?\d{1,2}?)?\s*[\$M¢£¥元圓€₹])|'
                        r'(?:(?:\d{1,3}[ ,]?)+[\.]\d{1,2}))(?:\s|$)')
        currency_matches=re.findall(currency_reg,t)

        if (len(currency_matches) != 0):
            for currency in currency_matches:
                t = t.replace(currency,' ', 1)
                entities_list.append('MONEY')
                # print(currency, " - MONEY")

        if (len(tax_matches) != 0):
            for tax in tax_matches:
                t = t.replace(tax,'', 1)
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
                t = re.sub(str(address), '', t)
                entities_list.append('ADR')
                # print(str(address), " - ADR1")

        elif len(short_address_matches) != 0:
            for address in short_address_matches:
                t = t.replace(str(address), '', 1)
                entities_list.append('ADR')
                # print(str(address), " - ADR")

        nlp = spacy.load("en_core_web_sm")
        # Changing default tokenizer to created
        nlp.tokenizer = self.custom_tokenizer(nlp)
        ruler = EntityRuler(nlp, overwrite_ents=True)

        patterns = [
            {"label": "TAX", "pattern": [{"TEXT": {"REGEX": "^(?![01][789]|2[89]|[46]9|7[089]|89|9[67])\d\d-\d{7}$"}}]},
            {"label": "EML", "pattern": [{"TEXT": {"REGEX": "^[-\w.]+@([A-z0-9][-A-z0-9]+\.)+[A-z]{2,4}$"}}]},
            {"label": "URL",
             "pattern": [{"TEXT": {"REGEX": "^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,6}&"}}]},
            {"label": "DATE", "pattern": [{"TEXT": {
             "REGEX": "^(19|20)\d\d-((0[1-9]|1[012])-(0[1-9]|[12]\d)|(0[13-9]|1[012])-30|(0[13578]|1[02])-31)$"}}]},
            {"label": "DATE", "pattern": [
             {"TEXT": {"REGEX": "^(0?[1-9]|[12][0-9]|3[01])[- /.](0?[1-9]|[12][0-9]|3[01])[- /.](19|20)\d\d$"}}]},
            {"label": "ZIP", "pattern": [{"TEXT": {"REGEX": "^\d{5}(?:[-\s]\d{4})?$"}}]},
            {"label": "TIME", "pattern": [{"TEXT": {"REGEX": "^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$"}}]},
            {"label": "MONEY", "pattern": [{'LOWER': {'IN': ['total','amount','subtotal','balance','USD','due','summary'
             'paid','dollars','cost','price']}},{"TEXT": {"REGEX": '\W'}, 'OP':'?'}, {"TEXT": {"REGEX": "(?:(\d{1,3}[ ,]?)+(?:[\.]\d{1,2})?)"}}]}
        ]
        ruler.add_patterns(patterns)
        # Priority of ruler
        nlp.add_pipe(ruler, before="ner")
        doc = nlp(t)

        for entity in doc.ents:
            entities_list.append(entity.label_)
            # print(entity.text, "-", entity.label_)
        print(sorted(entities_list))
    # Visualization in jupyter
    # displacy.render(doc, style="dep")
    # displacy.render(doc, style="ent")

        return sorted(entities_list)

    @staticmethod
    def compare_entities(entities_list, entities_list2):
        longest_entity_list = max(len(entities_list), len(entities_list2))

        matched_entities = list((Counter(entities_list) & Counter(entities_list2)).elements())
        differences_1 = list((Counter(entities_list) - Counter(matched_entities)).elements())
        differences_2 = list((Counter(entities_list2) - Counter(matched_entities)).elements())

        max_differences = max(len(differences_1), len(differences_2))
        final_score = 1 - (max_differences / longest_entity_list)

        # similarity coefficient
        print(final_score)

        if final_score < 0.65:
            print('NO')
        else:
            print('YES')


tex1 = ('Kathy Fink & Associates'
        ' $    5 643.76'
        ' 2342 East Broadway'
        ' phone:78787132123 TAX # 86-0813450')

tex2 = ('+6(089) / 636-48018'
        ' 2481 Es 22nd St TUCSON, AZ 34343'
        ' 5 March'
        ' Subtotal: 2324')

# comparing 2 texts
texts = EntityComparison(tex1, tex2)
texts.texts_reciever()

# only entity extracting
texts.entity_extract(tex1)

