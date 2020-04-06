"""
All the runtime state the bot will use.
"""

from abc import ABC, abstractmethod
from typing import List, Set
import json
from typing import NamedTuple, List
from random import choice, random
import os

from .pcomb import Left, Right
from ._types import Request, Response, QA
from .english import clause, parse_sentence_structure
from .english import SentenceStructure as S
from .fuzzy import fuzzy_in
from .synonyms import enlarge_keywords


# Used to return the assessment report of user input.
ChoiceVec = NamedTuple("ChoiceVec", (('role', str), ('tone', str)))


class Role:
    """
    super class for bot roles to provides role specific static data.
    """
    rolename = "generic"

    greeting = {
        "hi", "hello", "how", "are", "sup", "what's up"
    }

    censorwords = {
        "fuck", "shit", "dumb", "ass", "stupid", "retard",
    }

    negativity = {
        "not", "can't", "cannot", "couldn't", "could not"
    }

    keywords: Set[str] = set()


class Psychiatrist(Role):
    keywords = enlarge_keywords({
        "feel", "know",
        "doubtful", "lonely", "discouraged", "uncertain", "insulting",
        "ashamed", "indecisive", "sore",
        "hesitant", "vulnerable", "hateful", "dissatisfied",
        "empty", "unpleasant", "miserable", "detestable", "disillusioned",
        "frustrated", "resentful", "disgusting",
        "misgiving", "terrible", "lost", "pathetic", "unsure", "tragic",
        "uneasy", "bad", "die", "kill"
    })


class Depressed(Psychiatrist):
    rolename = "depressed"

    keywords = enlarge_keywords({
        "annoyed", "diminished", "embarrassed", "inferior", "upset",
        "depressed", "depression", "distressed", "disappointed",
        "disappointment", "upset", "incapable", "despair",
        "despicable", "distrustful",
        "powerless", "useless", "shy", "incompetent"
    }).union(Psychiatrist.keywords)


class PTSD(Role):
    rolename = "ptsd"

    keywords = enlarge_keywords({
        "past", "memory", "tramumataize", "suffer", "envision", "remember",
        "panic", "forget", "trigger", "lost", "disoriented", "disorder",
                "nightmare", "anxiety", "lost of interest", "distress",
                "distressing", "overprotective", "post", "traumatic", "trauma",
                "aggressive", "aggressive", "guilty", "abominable",
                "disgusting", "distrustful", "PTSD", "away", "ptsd"
    }).union(Psychiatrist.keywords)


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
        self.role_switcher = State.RoleSwitcher([Depressed(), PTSD()])
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
        wordlist = list(
            filter(
                lambda n: n is not None,
                (parsed.val[0]
                    if isinstance(parsed, Right)
                    else None)))
        if os.environ["DEBUG"] == "1":
            print(wordlist)
        tag = parse_sentence_structure(parsed)
        censor, negativity, greeting = State.ReqAnalyseVec(0, 0, 0)

        # precheck
        if wordlist:
            censor, negativity, greeting = self.assess(wordlist)

        if censor > 0.05:
            return Response(self.choice(ChoiceVec("generic", "negative")))

        if greeting > 0.65:
            return Response(self.choice(ChoiceVec("generic", "greeting")))

        if S.statement(tag):

            if random() > 0.75:
                res = self.choice(ChoiceVec("generic", "statement"))
            elif random() > 0.65:
                res = self.choice(ChoiceVec("generic", "confirmative"))
            else:  # determine role
                self.role_switcher.switch_role_by_stmt(self, req)
                res = self.choice(ChoiceVec(self.role.rolename, "statement"))

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

    def assess(self, wordlist: List[str]) -> 'State.ReqAnalyseVec':
        negativity = 0
        censor = 0
        greeting = 0
        n = len(wordlist) if len(wordlist) > 1 else 1
        for w in wordlist:
            if w in self.role.censorwords:
                censor += 1

            if w in self.role.negativity:
                negativity += 1

            if fuzzy_in(w, self.role.greeting):
                greeting += 1
        if os.environ["DEBUG"] == "1":
            print("asess: ", wordlist)
            print("asess: ",
                  State.ReqAnalyseVec(censor / n,
                                      negativity / n, greeting / n))

        return State.ReqAnalyseVec(censor / n, negativity / n, greeting / n)

    class RoleSwitcher:
        def __init__(self, roles: List[Role]):
            self.roles = roles

        def switch_role_by_stmt(self, state: 'State', stmt: str):
            state.switch_role(self.best_fit(stmt))

        def best_fit(self, statement: str) -> Role:
            indexes = [
                (self.keyword_idx(statement, role), role)
                for role in self.roles
            ]
            index, role = max(indexes, key=lambda p: p[0])
            if os.environ["DEBUG"] == "1":
                print(role)
            return role

        def keyword_idx(self, statement: str, role: Role) -> float:
            """
            the percentage of words in keyword list
            Fuzzied with levenshtien.
            """
            stmt_words = statement.strip().split(" ")
            hitted_words = [
                w for w in stmt_words
                if fuzzy_in(w, role.keywords)
            ]
            return len(hitted_words) / len(stmt_words)
