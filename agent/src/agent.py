from typing import Optional
from ._types import Request, Response, QA
from .state import Role
from .state import State
from .state import Depressed
from .state import PTSD


class Agent:
    """
    For creating a new bot entity.
    Handling the repl conversation.
    """

    role_menu = """
    1. Depress
    2. Psychiatrist
    3. Celebrity
    4. Friend
    """

    def __init__(self):
        self.role: Optional[Role] = None
        self.state = State("static/dictoinary.json")

    def run(self):
        """ selection root """
        # entrance of the bot
        # print("Hi there. What do you want me to be?")
        print("<-Psychiatrist specialized on depression and PTSD->")
        print("<-Shift topic as you go->")
        print("<-press q to exit program->")
        # print(Agent.role_menu)
        self.session_start()

    def session_start(self):
        print("enter q to exit talk")
        print("I'm a bot psychiatrist. How are you?")
        while True:
            req: Request = input("> ")

            if req == "q":
                break

            res: Response = self.state.eat(req.lower())
            print(f"bot> {res}")

