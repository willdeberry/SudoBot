from flask import Flask, jsonify, request, abort
from discord_interactions import verify_key_decorator, InteractionType, InteractionResponseType
import requests
import os

from dotenv import load_dotenv
load_dotenv()

from commands import DiscordCommands
from parse_commands import CommandResponse


app = Flask(__name__)
public_key = os.environ.get('PUBLIC_KEY')


DiscordCommands().register_commands()


@app.route('/', methods = ['POST', 'GET'])
@verify_key_decorator(public_key)
def main():
    if request.method == 'GET':
        return 'Hello'

    if request.method == 'POST':
        print(request.json)
        response = CommandResponse(request.json)
        if request.json["type"] == 1:
            return jsonify({"type": 1})
        else:
            return jsonify({
                "type": 3,
                "data": {
                    "tts": False,
                    "content": response.parse_response(),
                    "embeds": [],
                    "allowed_mentions": []
                }
            })


if __name__ == '__main__':
    app.run(host = '0.0.0.0')
