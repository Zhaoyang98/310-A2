"""
A Parser combinator resemble haskell parsec.
"""
import string
from abc import ABC, abstractmethod
from typing import Callable, Any, Generic, TypeVar, cast
from typing import Tuple, List, Union, Sequence
from functools import reduce
from itertools import chain
import string as _string

T = TypeVar('T')
U = TypeVar('U')
L = TypeVar('L')
R = TypeVar('R')
VarArgCallable = TypeVar("VarArgCallable", bound=Callable[..., Any])
Pair = Tuple[T, U]


def flatten(l): return [
    item
    for sublist in l
    for item in (
        sublist if isinstance(sublist, list) else [sublist])]


class Functor(ABC, Generic[U]):
    """ functor typeclass """
    @abstractmethod
    def fmap(self, f: Callable) -> 'Functor[U]':
        ...


class Either(Functor, Generic[L, R]):
    ...


class Left(Either):
    def __init__(self, errmsg):
        self.errmsg = errmsg

    def __str__(self):
        return "(Left %s)" % self.errmsg

    __repr__ = __str__

    def __eq__(self, other):
        if not isinstance(other, Left):
            return NotImplementedError
        return self.errmsg == other.errmsg

    def fmap(self, f):
        return self


class Right(Either):
    def __init__(self, val):
        self.val = val

    def unwrap(self):
        return self.val

    @property
    def val0(self):
        """ shove into list """
        if isinstance(self.val[0], list):
            return flatten(self.val[0])
        else:
            return [self.val[0]]

    def __str__(self):
        return "(Right %s)" % str(self.val)

    __repr__ = __str__

    def __eq__(self, other):
        if not isinstance(other, Left):
            return NotImplementedError
        return self.errmsg == other.errmsg

    def fmap(self, f):
        return Right((f(self.val0), self.val[1]))


class Parser(Functor[U]):
    def __init__(self, f: Callable):
        self.f = f
        self._discarded = False

    def parse(self, *args, **kwargs):  # push whatever state.
        return self.f(*args, **kwargs)

    def __rshift__(self, rparser):
        return then(self, rparser)

    def __lshift__(self, rparser):
        return then(self, rparser)

    def __or__(self, rparser):
        return otherwise(self, rparser)

    def __mul__(self, times):
        return n(self, times)

    def fmap(self, transformer):
        return Parser(
            lambda *args, **kwargs: (
                self.f(*args, **kwargs).fmap(transformer)))

    def discard(self):
        self._discarded = True
        return self

    __call__ = parse


def run_parser(p, inp):
    return p(inp)


def valcheck(v) -> bool:
    if isinstance(v, str) and not v.strip():
        return False
    if isinstance(v, list) and v and v[0] == "":
        return False
    return True


def then(p1: Parser, p2: Parser) -> Parser:
    @Parser
    def parse(s):
        res1 = p1(s)
        if isinstance(res1, Left):
            return res1
        else:
            res2 = p2(res1.val[1])  # parse remaining chars.
            if isinstance(res2, Right):
                v1 = res1.val0
                v2 = res2.val0
                vs = []
                if not p1._discarded and valcheck(v1):
                    vs += v1
                if not p2._discarded and valcheck(v2):
                    vs += v2

                return Right((vs, res2.val[1]))
            return res2
    return parse


def n(parser: Parser, count: int) -> Parser:
    @Parser
    def parse(s):
        fullparsed = ""
        for i in range(count):
            res = parser(s)
            if isinstance(res, Left):
                return res
            else:
                parsed, remaining = res.unwrap()
                s = remaining
                fullparsed += parsed
        return Right((fullparsed, s))
    return parse


def otherwise(p1: Parser, p2: Parser) -> Parser:
    @Parser
    def parse(s):
        res = p1(s)
        if isinstance(res, Right):
            return res
        else:
            res = p2(s)
            if isinstance(res, Right):
                return res
            else:
                return Left("Failed at both")
    return parse


def char(c: str) -> Parser:
    @Parser
    def parse(s):
        if not s:
            msg = "S is empty"
            return Left(msg)
        else:
            if s[0] == c:
                return Right((c, s[1:]))
            else:
                return Left("Expecting '%s' and found '%s'" % (c, s[0]))
    return parse


def anyof(parsers: List[Parser]) -> Parser:
    return reduce(otherwise, parsers)


def strg(s: str):
    return reduce(then, list(map(char, list(s)))).fmap(lambda l: "".join(l))


def inchars(chars: Sequence):
    return anyof(list(map(char, chars)))


def until_seq(seq: Sequence) -> Parser:
    @Parser
    def parse(s):
        if not s:
            msg = "S is empty"
            return Left(msg)
        else:
            if seq == s[:len(seq)]:
                return Right(("", s))
            else:
                return Left(f"Expecting {seq} and found {s[:len(seq)]}")
    return parse


def until(p: Parser) -> Parser:
    @Parser
    def parse(s):
        res = p(s)
        if isinstance(res, Left):
            return res
        else:
            return Right(("", s))
    return parse


def many(p: Parser) -> Parser:
    def zero_or_more(p, inp) -> Tuple:
        res = p(inp)
        if isinstance(res, Left):
            return "", inp
        else:
            car, cdr = res.val
            cdar, cddr = zero_or_more(p, cdr)
            values = car
            if cdar:
                if isinstance(car, str):
                    values = car+cdar
                elif isinstance(car, list):
                    values = car + (
                        [cdar] if isinstance(cdar, str) else cdar)
            return values, cddr

    @Parser
    def parse(s):
        return Right(zero_or_more(p, s))
    return parse


def sep_by1(sep: Parser, p: Parser) -> Parser:
    return p >> many(sep >> p)


def sep_by(sep, parser):
    return (sep_by1(sep, parser) | Parser(lambda x: Right(([], ""))))


def many1(p: Parser) -> Parser:
    @Parser
    def parse(s):
        res = run_parser(p, s)
        if isinstance(res, Left):
            return res
        else:
            return run_parser(many(p), s)
    return parse


def optional(p: Parser):
    noneparser: Parser = Parser(lambda x: Right((None, "")))
    return otherwise(p, noneparser)


def forward(parsergeneratorfn):
    def parse(s):
        return parsergeneratorfn()(s)
    return parse


letter = inchars(string.ascii_letters)
lletter = inchars(string.ascii_lowercase)
uletter = inchars(string.ascii_uppercase)
digit = inchars(string.digits)
digits = many1(digit)
whitespace = inchars(string.whitespace)
ws = whitespace.discard()
letters = many1(letter)
