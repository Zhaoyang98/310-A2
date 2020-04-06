"""
Simulate two bots talking with each other.

bot1 runs on the local machine.
bot2 is running on a remote server.

To run bot2 on the local machine use --local and --socket N to specify a socket
"""

from src.state import State
from app import create_pairs
from time import sleep

import requests
import argparse

API = 'https://cosc310-bot.herokuapp.com'
DICTIONARY_PATH = 'static/dictoinary.json'


def parseargs():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--local', type=bool)
    parser.add_argument('--socket', type=int, default=5000)
    parser.add_argument('--iterations', type=int, default=50)
    return parser.parse_args()


def talk(api: str, state: State, message: str):
    url = f'{api}/agent/{message}'
    req = requests.post(url)
    state.history = create_pairs(req.json())
    return state.history[-1]


if __name__ == '__main__':
    args = parseargs()

    if args.local:
        api = f'localhost:{args.socket}'
    else:
        api = API

    try:
        message = 'Hello'
        state = State(DICTIONARY_PATH)
        for i in range(args.iterations):
            if i % 2 == 0:
                print('bot1:', message)
            else:
                print('bot2:', message, '\n')
            req, res = talk(api, state, message)
            sleep(0.5)
            message = res
    except KeyboardInterrupt:
        pass
