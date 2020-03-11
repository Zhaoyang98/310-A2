import json
from typing import Optional, List, cast
from .pcomb import Either, Left, Right
from .pcomb import char, letters, ws, sep_by, until
from .pcomb import otherwise, anyof, many1, strg, optional


def readwords(fname: str) -> list:
    words = []
    with open(fname, "r") as f:
        words = list(map(lambda w: w.strip(), f.readlines()))
    return words


# load words


def inwords(wordlist):  # generate parsers for words
    return anyof(list(map(strg, wordlist)))


# puncuation
comma = char(",")
period = char(".")
prime = char("'")
questionmark = char("?")
linebreak = char("\n")


questionword = inwords(
    ["didn't",
     "don't",
     "doesnt",
     "didnt",
     "what's",
     "what're",
     "won't",
     "wouldn't",
     "can't"
     "could't"
     "do",
     "what",
     "why",
     "will",
     "when",
     "how",
     "where",
     "can",
     "can not",
     "dont",
     "does",
     "did"])
bewords = inwords(
    [
        "weren't",
        "isn't",
        "aren't",
        "wasn't",
        "is",
        "are",
        "am",
        "am not",
        "be",
        "was",
        "was not",
        "were",
    ])
_verb = inwords(readwords("static/verb"))
_pronoun = inwords(readwords("static/pronoun"))
_noun = inwords(readwords("static/noun"))
_adjective = inwords(readwords("static/adjective"))
_adverb = inwords(readwords("static/adverb"))
_preposition = inwords(readwords("static/preposition"))


article = inwords(["a", "an", "the"])
pronoun = _pronoun
adjective = _adjective
adverb = _adverb
noun = _noun
nounclause = (noun
              | adjective >> noun
              | pronoun
              | article >> noun
              | article >> adjective >> noun
              )
adjectiveclause = adjective | adverb >> adjective
verb = (_verb
        | adverb >> _verb)

# basic elements
anyword = letters | (prime * 1)
word = (noun
        | questionword
        | bewords
        | verb
        | adjective
        | adverb
        | article
        | anyword
        )
words = sep_by(ws, word)
clause = words >> optional(comma)

# TODO make it true parser combinator.

# sentence structure
W = char("W")
N = char("N")
P = char('P')
V = char("V")
A = char("A")
D = char("D")
T = char("T")
X = char("X")

# statements
PWV = P >> W >> V        # i dont know
PVA = P >> V >> A        # i feel lonely or i like rice
PVP = P >> V >> P
NVN = N >> V >> N

WPNP = W >> P >> N >> P  # can you do xx?
WVPV = W >> V >> P >> V  # what do you like
WWPV = W >> W >> P >> V  # what can you do


class SentenceStructure:
    """
    sentence structure for english.
    """
    statement = (PWV
                 | PVA
                 | PVP
                 | NVN
                 )

    question = (WPNP
                | WVPV
                | WWPV
                )


def exthuasted(r: Either):
    if isinstance(r, Left):
        return False
    return cast(Right, r).val[1] == ""


# check sentence structure.
def parse_sentence_structure(res: Either):
    """
    construct sentence structure tags.
    """
    if isinstance(res, Left):
        return None
    if isinstance(res, Right):
        wordlist, _ = cast(Right, res).val
        tags: List = []
        for w in wordlist:
            if exthuasted(questionword(w)):
                tags.append('W')
            elif exthuasted(pronoun(w)):
                tags.append('P')
            elif exthuasted(noun(w)):
                tags.append('N')
            elif exthuasted(verb(w)):
                tags.append('V')
            elif exthuasted(adjective(w)):
                tags.append('A')
            elif exthuasted(adverb(w)):
                tags.append('D')
            elif exthuasted(article(w)):
                tags.append('T')
            else:
                tags.append('X')

        tagstr = "".join(filter(lambda x: x != 'X', tags))
        return tagstr
