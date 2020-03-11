"""
All the runtime state the bot will use.
"""

from abc import ABC, abstractmethod
from typing import List
import json
from typing import NamedTuple
from random import choice, random

from .pcomb import Left, Right
from ._types import Request, Response, QA
from .english import clause, parse_sentence_structure
from .english import SentenceStructure as S


class Role:
    """
    super class for bot roles to provides role specific static data.
    """
    rolename = "generic"

    greeting = [
        "hi", "hello", "how", "are", "you", "sup", "what's up"
    ]

    censorwords = [
        "fuck", "shit", "dumb", "ass", "stupid", "retard", "hate",
    ]

    negativity = [
        "not", "can't", "cannot", "couldn't", "could not"
    ]


class Psychiatrist(Role):
    rolename = "psychiatrist"

    keywords = [
        "feel", "know", "upset", "incapable", "enraged", "disappointed",
        "doubtful", "alone", "discouraged", "uncertain", "insulting",
        "ashamed", "indecisive", "sore", "powerless", "useless",
        "annoyed", "diminished", "embarrassed", "inferior", "upset",
        "guilty", "hesitant", "vulnerable", "hateful", "dissatisfied",
        "shy", "empty", "unpleasant", "miserable", "forced",
        "offensive", "detestable", "disillusioned", "bitter",
        "unbelieving", "despair", "aggressive", "despicable", "skeptical",
        "frustrated", "resentful", "disgusting", "distrustful",
        "distressed", "abominable", "misgiving", "provoked", "terrible",
        "lost", "pathetic", "despair", "unsure", "tragic", "infuriated",
        "uneasy", "cross", "bad"
    ]


class Production(Role):
    rolename = "callagent"


class Celebrity(Role):
    rolename = "celebrity"


class Friend(Role):
    rolename = "friend"


# Used to return the assessment report of user input.
ChoiceVec = NamedTuple("ChoiceVec", (('role', str), ('tone', str)))


class State(ABC):
    """
    define the conversation state
    """

    class ReqAnalyseVec(NamedTuple):
        censor_rate: float
        negativity: float
        greeting: float

    def __init__(self, dictname: str):
        self.history: List[QA] = []
        self.role: Role = Role()
        with open(dictname, 'r') as f:
            self.dict = json.loads(f.read())

    def switch_role(self, r: Role):
        self.role = r

    def eat(self, req: Request) -> Response:
        res = self.eval(req)
        self.history.append(QA(req, res))
        return res

    def eval(self, req: Request) -> Response:
        res: str = ""
        parsed = clause(req)
        wordlist = parsed.val[0] if isinstance(parsed, Right) else None
        tag = parse_sentence_structure(parsed)

        # precheck
        if wordlist:
            censor, negativity, greeting = self.assess(wordlist)

        if censor > 0.05:
            return Response(self.choice(ChoiceVec("generic", "negative")))

        if greeting > 0.7:
            return Response(self.choice(ChoiceVec("generic", "greeting")))

        if S.statement(tag):

            if random() > 0.75:
                res = self.choice(ChoiceVec("generic", "statement"))
            elif random() > 0.5:
                res = self.choice(ChoiceVec("generic", "confirmative"))
            else:
                res = self.choice(ChoiceVec("psychiatrist", "statement"))

        elif S.question(tag):
            if random() > 0.5:
                if negativity > 0.2:
                    res = self.choice(ChoiceVec("generic", "positive"))
                else:
                    res = self.choice(ChoiceVec("generic", "negative"))

            else:  # usually say something nice
                res = self.choice(ChoiceVec("generic", "positive"))

        else:
            res = self.choice(ChoiceVec("generic", "confused"))

        return Response(res)

    def choice(self, chvec: ChoiceVec) -> Response:
        role, tone = chvec
        replies = self.dict[role][tone]

        if isinstance(replies, list):
            return choice(replies)
        return Response("...")

    def assess(self, wordlist: list) -> 'State.ReqAnalyseVec':
        negativity = 0
        censor = 0
        greeting = 0
        n = len(wordlist) - 1 if len(wordlist) > 1 else 1
        for w in wordlist:
            if w in self.role.censorwords:
                censor += 1
            if w in self.role.negativity:
                negativity += 1
            if w in self.role.greeting:
                greeting += 1

        return State.ReqAnalyseVec(censor / n, negativity / n, greeting / n)
