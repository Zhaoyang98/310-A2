import unittest
from agent.src.fuzzy import levenshtien
from agent.src.fuzzy import fuzzy
from agent.src.fuzzy import fuzzy_in


class TestFuzzy(unittest.TestCase):
    def test_leveinshtein(self):
        res = levenshtien("goo0d", "goo0b")
        self.assertTrue(res == 1.0)

    def test_fuzzy(self):
        res = fuzzy("test", "test")
        self.assertTrue(res is not None)

    def test_fuzyy_in(self):
        s = set({"a", "set", "of", "different", "words"})
        self.assertTrue(fuzzy_in("differnt", s))


