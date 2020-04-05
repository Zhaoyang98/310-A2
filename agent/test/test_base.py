import unittest
from src.pcomb import Left, Right, Parser
from src.pcomb import run_parser, char, inchars, strg
from src.pcomb import anyof, until_seq, until, sep_by, sep_by1
from src.pcomb import many, many1, optional
from src.pcomb import digits, ws

class TestParsers(unittest.TestCase):

    def test_parser_init(self):
        """ parser alone should apply function to parsed text """
        p = Parser(lambda s: s + "str")
        res: str = p("a")
        self.assertEqual(res, "astr")

    def test_parser_fmap(self):
        """
        fmap should propagate the lambda to innder functor.
        """
        p = Parser(lambda s: Right(("a", "bcde"))).fmap(lambda x: x[0] + "x")
        res: Right[str] = p("abc")
        self.assertEqual(res, Right(("ax", "bcde")))

    def test_run_parser(self):
        p = Parser(lambda s: s + "a")
        self.assertEqual(run_parser(p, "a"), "aa")

    def test_pcomb_char(self):
        """ test the basic parse combination """
        c = char("a")
        self.assertEqual(c("abcd"), Right(("a", "bcd")))

    def test_pcomb_then(self):
        c1 = char("a")
        c2 = char("b")
        c3 = char("c")
        c = c1 >> c2 >> c3
        self.assertEqual(c("abcde"), Right((["abc"], "de")))

    def test_pcomb_otherwise(self):
        c1 = char("a")
        c2 = char("b")
        c = c1 | c2
        self.assertEqual(c("abc"), Right(("a", "bc")))
        self.assertEqual(c("bbc"), Right(("b", "bc")))

    def test_pcomb_ntimes(self):
        c1 = char("a")
        c = c1 * 3
        self.assertEqual(c("aaaab"), Right(("aaa", "ab")))

    def test_pcomb_anyof(self):
        c1 = char("a")
        c2 = char("b")
        c3 = char("c")
        c = anyof([c1, c2, c3])
        self.assertEqual(c("abc"), Right(("a", "bc")))
        self.assertEqual(c("bbc"), Right(("b", "bc")))
        self.assertEqual(c("cbc"), Right(("c", "bc")))

    def test_pcomb_inchars(self):
        c = inchars(["a", "b", "c"])
        self.assertEqual(c("abc"), Right(("a", "bc")))
        self.assertEqual(c("bbc"), Right(("b", "bc")))
        self.assertEqual(c("cbc"), Right(("c", "bc")))

    def test_pcomb_string(self):
        c = strg("good")
        self.assertEqual(c("good morning"), Right(("good", "morning")))

    def test_pcomb_until_seq(self):
        c = until_seq("xx")
        self.assertEqual(c("xxabc"), Right(("", "xxabc")))

    def test_pcomb_until(self):
        c = until(char("x"))
        self.assertEqual(c("xxabc"), Right(("", "xxabc")))

    def test_pcomb_many(self):
        """ should return Right for 0 to many matches"""
        c = many(char("a"))
        self.assertEqual(c("aaaaaaaaaabbbb"), Right(("aaaaaaaaaa", "bbbb")))
        self.assertEqual(c("bb"), Right(("", "bb")))

    def test_pcomb_many1(self):
        """ should return Left if there is no match"""
        c = many1(char("a"))
        self.assertEqual(c("aaaaaaaaaabbbb"), Right(("aaaaaaaaaa", "bbbb")))
        self.assertTrue(isinstance(c("bb"), Left))

    def test_pcomb_sep_by1(self):
        c = sep_by1(char(",").discard(), many(char("a") >> char("b")))
        self.assertTrue(c("ababaa"), Right((["a", "b", "a", "b"], "aa")))

    def test_pcomb_sep_by(self):
        c = sep_by(char(",").discard(), many(char("a") | char("b")))
        self.assertTrue(c("ababx"), Right((["a", "b", "a", "b"], "x")))

    def test_pcomb_sep_by_digits(self):
        c = sep_by(char("|").discard(), many(digits))
        self.assertTrue(c("123|78|23x"), Right((["123", "78", "23"], "x")))

    def test_pcomb_option(self):
        """ return None if there is no match """
        c = optional(char("a"))
        self.assertEqual(c("bc"), Right((None, "")))


