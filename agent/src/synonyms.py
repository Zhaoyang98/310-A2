from nltk.corpus import wordnet
from itertools import chain
from typing import Set


def enlarge_keywords(keywords: Set[str]) -> Set[str]:
    enlarged: Set[str] = set()
    for word in keywords:
        syns = wordnet.synsets(word)
        s = set(
            chain.from_iterable([
                syn.lemma_names()
                for syn in syns
            ]))
        enlarged = enlarged.union(s)
    return enlarged



