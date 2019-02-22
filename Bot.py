import json
import time
from typing import Dict

import requests

url = "https://api.telegram.org/bot{token}/{method}"
token = "262354959:AAGZbji0qOxQV-MwzzRqiWJYdPVzkqrbC4Y"
lampo = 89675136
sara = 272556084


def execute(method: str, **params: Dict):
    request = requests.get(url.format(token=token, method=method), params=params)
    if request.ok:
        return request.json()['result']
    else:
        print(request.json())
        print(request.json()['error'])
        return None


def main():
    last_update = 0
    while True:
        updates = execute("getUpdates", offset=last_update)
        for update in updates:
            print(update)
            execute("sendMessage", chat_id=update['message']['from']['id'], text=json.dumps(update, indent=2, sort_keys=True))
        last_update = updates[-1]['update_id'] + 1 if len(updates) > 0 else last_update
        time.sleep(1)


if __name__ == "__main__":
    main()
