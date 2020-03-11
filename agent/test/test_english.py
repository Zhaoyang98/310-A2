import unittest
from src.pcomb import Left, Right, Parser
from src.pcomb import run_parser, char, inchars, strg
from src.pcomb import anyof, until_seq, until, sep_by, sep_by1
from src.pcomb import many, many1, optional
from src.pcomb import digits, ws
import src.english as E


class TestParseEnglish(unittest.TestCase):
    """ all input will be treated as lower case """

    def test_adverb(self):
        res = E.adverb("well")
        self.assertEqual(res, Right(("well", "")))

    def test_adjective(self):
        res = E.adjective("ideal")
        self.assertEqual(res, Right(("ideal", "")))

    def test_verb(self):
        res = E.adjective("think")
        self.assertEqual(res, Right(("think", "")))

    def test_noun(self):
        res = E.adjective("sea")
        self.assertEqual(res, Right(("sea", "")))

    def test_word(self):
        res = E.word("bread")
        self.assertEqual(res, Right(("bread", "")))

    def test_words(self):
        res = E.words("bread is good")
        self.assertEqual(res, Right((["bread", "is", "good"], "")))

    def test_clause(self):
        res = E.clause("i am fine, thx.")
        self.assertEqual(res, Right((["i", "am", "fine"], "thx")))

    def test_tags(self):
        s = ["hi",
             "i don't know what to do",
             "can you help me?",
             "i feel lonely",
             "i wll go home later",
             "i am not happy",
             "what do you like?",
             "what can you do?",
             "they dont like me",
             "she opened the door",
             ]

        for x in s:
            print(x, E.parse_sentence_structure(E.clause(x)))
            print("---")
