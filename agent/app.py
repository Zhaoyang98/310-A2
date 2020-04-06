from flask import Flask, request
from flask_cors import CORS
#from flask_basicauth import BasicAuth
from src.state import State
from itertools import chain, tee
from typing import List, Tuple

import json

app = Flask(__name__)
app.config['BASIC_AUTH_USERNAME'] = 'COSC_310'
app.config['BASIC_AUTH_PASSWORD'] = 'group27'
cors = CORS(app)

DICTIONARY_PATH = 'static/dictoinary.json'


@app.route('/agent/<message>', methods=['GET'])
# @basic_auth.required
def start_conversation(message):
    state = State(DICTIONARY_PATH)
    state.eat(message.lower())
    return json.dumps(flatten_pairs(state.history))


@app.route('/agent/<message>', methods=['POST'])
# @basic_auth.required
def continue_conversation(message):
    history = request.get_json()
    state = State(DICTIONARY_PATH)

    if history:
        state.history = create_pairs(history)

    state.eat(message.lower())
    return json.dumps(flatten_pairs(state.history))


def create_pairs(flat_history: List[str]) -> List[Tuple[str, str]]:
    state = State(DICTIONARY_PATH)
    req, res = tee(flat_history)
    next(res, None)
    return list(zip(req, res))


def flatten_pairs(history: List[Tuple[str, str]]) -> List[str]:
    return list(chain.from_iterable(history))

