import unittest
import json
from src.toneselector import ToneSelector
from src.state import Psychiatrist


class TestToneSelector(unittest.TestCase):
    dictname = "static/dictoinary.json"

    def setUp(self):
        with open(TestToneSelector.dictname, 'r') as f:
            self.d = json.loads(f.read())
        self.state = Psychiatrist()
        self.ts = ToneSelector(
            TestToneSelector.dictname,
            Psychiatrist)

    def test_choice(self):
        res = self.ts.choice(self.ts.rolename, "statement")
        self.assertTrue(res in self.d[self.ts.rolename]["statement"])

