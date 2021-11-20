
def build_message(title, fields):
    return {
        "type": 4,
        "data": {
            "tts": False,
            "content": "",
            "embeds": [
                {
                    "title": title,
                    "fields": fields
                }
            ],
            "allowed_mentions": []
        }
    }

def build_adv_message(title, embeds):
    default_embed = [{'title': title, 'fields': []}]
    print(default_embed.extend(embeds))
    return {
        "type": 4,
        "data": {
            "tts": False,
            "content": "",
            "embeds": default_embed,
            "allowed_mentions": []
        }
    }
