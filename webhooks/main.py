
from flask import Flask, request, Response
from plex import Plex


app = Flask(__name__)


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


if __name__ == '__main__':
    app.run(host = '0.0.0.0')
