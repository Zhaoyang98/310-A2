from typing import NewType, NamedTuple
from collections import namedtuple

Response = NewType('Response', str)  # from bot
Request = NewType('Request', str)    # from talker


class QA(NamedTuple):
    req: Request
    res: Response
