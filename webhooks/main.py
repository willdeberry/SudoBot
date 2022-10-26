
import aiohttp
from flask import Flask, jsonify, request, abort, Response
from discord_interactions import verify_key_decorator
import requests
import os
from dotenv import load_dotenv

from plex import Plex
from responses import CommandResponse


load_dotenv()
app = Flask(__name__)
public_key = os.environ.get('PUBLIC_KEY')


@app.route('/plex', methods = ['POST'])
async def plex():
    payload = request.form.to_dict()
    print(payload)
    plex = Plex()
    await plex.handle_event(payload)
    return Response(status = 204)


@app.route('/status', methods = ['GET'])
def status():
    return Response(status = 204)


@app.route('/', methods = ['POST'])
@verify_key_decorator(public_key)
def main():
    response = CommandResponse(request.json)
    if request.json["type"] == 1:
        return jsonify({"type": 1})
    else:
        return jsonify(response.parse_response())


if __name__ == '__main__':
    app.run(host = '0.0.0.0')
