from typing import Optional
from ._types import Request, Response, QA
from .state import Role
from .state import State
from .state import Psychiatrist
from .state import Production
from .state import Celebrity
from .state import Friend


class Agent:
    """
    For creating a new bot entity.
    Handling the repl conversation.
    """

    role_menu = """
    1. Call agent center
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
        while True:
            # print("Hi there. What do you want me to be?")
            # print("press q to exit program")
            # print(Agent.role_menu)
            self.session_start()
            print("enter q to quit program ")
            choice: Request = input("> ")
            if choice == "q":
                break

            # elif int(choice) not in range(1, 5):
            #     print("Sorry please enter 1 - 5")
            #     continue

    def session_start(self):
        print("enter q to exit talk")
        print("I'm a bot psychiatrist. How are you?")
        while True:
            req: Request = input("> ")

            if req == "q":
                break

            res: Response = self.state.eat(req.lower())
            print(f"bot> {res}")

    def state_init(self, choice: int):
        assert choice in range(1, 5)

        if choice == 1:
            self.state = Psychiatrist()

        elif choice == 2:
            self.state = Production()

        elif choice == 3:
            self.state = Celebrity()

        elif choice == 4:
            self.state = Friend()
