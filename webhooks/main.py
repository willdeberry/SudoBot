
from flask import Flask, jsonify, request, abort
from discord_interactions import verify_key_decorator, InteractionType, InteractionResponseType
import requests
import os
from dotenv import load_dotenv

from responses import CommandResponse


load_dotenv()
app = Flask(__name__)
public_key = os.environ.get('PUBLIC_KEY')


@app.route('/status', methods = ['GET'])
def status():
    return 'Alive'


@app.route('/', methods = ['POST'])
@verify_key_decorator(public_key)
def main():
    print(request.json)
    response = CommandResponse(request.json)
    if request.json["type"] == 1:
        return jsonify({"type": 1})
    else:
        return jsonify(response.parse_response())


if __name__ == '__main__':
    app.run(host = '0.0.0.0')
