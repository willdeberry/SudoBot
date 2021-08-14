
def build_message(title, fields):
    return {
        "type": 4,
        "data": {
            "tts": False,
            "content": "",
            "embeds": [
                {
                    "title": title,
                    "type": "rich",
                    "fields": fields
                }
            ],
            "allowed_mentions": []
        }
    }
