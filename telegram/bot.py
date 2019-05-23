import json
import time
from typing import Dict, List

import requests

import commands.command as command
from telegram.wrappers import Update, Command, Chat, Message


class Bot:
    url = "https://api.telegram.org/bot{token}/{method}"
    lampo = 89675136
    sara = 272556084

    def __init__(self, token: str):
        self.token = token

    def __execute(self, method: str, **params) -> Dict:
        """
        Esegue una httprequest con il metodo prescelto

        :param method: nome del metodo da eseguire
        :param params: parametri del metodo da eseguire
        :return: il contenuto della risposta oppure l'errore
        """
        request = requests.get(self.url.format(token=self.token, method=method), params=params)
        if request.ok:
            return request.json()['result']
        else:
            print(request.json())
            print(request.json().get('error', request.json().get('description', request.json())))

            return {}

    def get_updates(self, last_update=0) -> List[Update]:
        """
        Cerca se ci sono stati update dall'ultima volta che sono stati controllati

        :param last_update: id dell'ultimo update
        :return: la lista, eventualmente vuota, di update
        """
        updates = self.__execute("getUpdates", offset=last_update)

        return [Update.from_dict(update) for update in updates]

    def send_message(self, chat_id: int, text: str, parse_mode: str = "HTML", reply_to: int = None,
                     keyboard: Dict = None) -> Dict:
        """
        Manda un messaggio di testo con eventuale tastiera

        :param chat_id: a chi mandare il messaggio
        :param text: il testo da mandare
        :param parse_mode: Markdown o HTML
            Markdown *...* (grassetto) _..._ (corsivo) [nome_url](url_effettivo) [utente](tg://user?id=...)
            `...` (code) ```...``` (block)
            HTML <b>...</b> (grassetto) <i>...</i> (corsivo) <a href="url">nome_url</a>
            <a href="tg://user?id=...">utente</a> <code>...</code> <pre>...</pre>
        :param reply_to: id del messaggio
        :param keyboard: tastiera da mostrare eventualmente
        :return:
        """
        return self.__execute("sendMessage", chat_id=chat_id, text=text, parse_mode=parse_mode,
                              reply_to_message_id=reply_to, reply_markup=keyboard)

    def forward_message(self, chat_id: int, from_chat: Chat, message: Message):
        """
        Inoltra un messaggio

        :param chat_id: a chi inoltrare il messaggio
        :param from_chat: da dove arriva il messaggio
        :param message: il messaggio da inoltrare
        :return:
        """
        return self.__execute("forwardMessage", chat_id=chat_id, from_chat_id=from_chat.chat_id, message_id=message.message_id)

    def polling(self, last_update: int = 0, wait: int = 1):
        while True:
            updates = self.get_updates(last_update)
            for update in updates:
                print(update)
                if update.message.reply_to and update.message.reply_to.original_from_user:
                    self.forward_message(update.message.reply_to.original_from_user.user_id, update.message.chat, update.message)
                elif isinstance(update.message, Command):
                    command.execute(self, update)
                else:
                    self.send_message(update.message.chat.chat_id, json.dumps(update.update, indent=2, sort_keys=True))
            last_update = updates[-1].update_id + 1 if len(updates) > 0 else last_update
            time.sleep(wait)

    def discard(self):
        updates = self.get_updates()
        self.polling(updates[-1].update_id + 1 if len(updates) > 0 else 0)


def main():
    bot = Bot("262354959:AAGZbji0qOxQV-MwzzRqiWJYdPVzkqrbC4Y")
    bot.polling()


if __name__ == "__main__":
    main()
