import json
from typing import Dict, List

import requests

from telegram.ids import lampo
from telegram.wrappers import Update, Chat, Message, Keyboard


class Bot:
    url = "https://api.telegram.org/bot{token}/{method}"

    def __init__(self, token: str):
        self.token = token

    def __execute(self, method: str, **params) -> Dict:
        """
        Esegue una httprequest con il metodo

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

    def dump(self, to: int = lampo, *args, **kwargs) -> Dict:
        return self.send_message(to, json.dumps(args, indent=2, sort_keys=True) + "\n" + json.dumps(kwargs, indent=2,
                                                                                                    sort_keys=True))

    def get_updates(self, last_update=0) -> List[Update]:
        """
        Cerca se ci sono stati update dall'ultima volta che sono stati controllati

        :param last_update: id dell'ultimo update
        :return: la lista, eventualmente vuota, di update
        """
        updates = self.__execute("getUpdates", offset=last_update)

        return [Update.from_dict(update) for update in updates]

    def send_message(self, chat_id: int, text: str, parse_mode: str = "HTML", reply_to: int = None,
                     keyboard: Keyboard = Keyboard()) -> Dict:
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
                              reply_to_message_id=reply_to, reply_markup=keyboard.to_json())

    def edit_message(self, chat_id: int, message_id: int, text: str, parse_mode: str = "HTML",
                     keyboard: Keyboard = Keyboard()) -> Dict:
        """
        Edita un messaggio precedentemente inviato

        :param chat_id: chat dov'è presente il messaggio
        :param message_id: id del messaggio da modificare
        :param text: il nuovo testo del messaggio
        :param parse_mode: Markdown o HTML
        :param keyboard: la nuova tastiera da mostrare eventualmente
        :return:
        """
        return self.__execute("editMessageText", chat_id=chat_id, message_id=message_id,
                              text=text, parse_mode=parse_mode, reply_markup=keyboard.to_json())

    def forward_message(self, chat_id: int, from_chat: Chat, message: Message):
        """
        Inoltra un messaggio

        :param chat_id: a chi inoltrare il messaggio
        :param from_chat: da dove arriva il messaggio
        :param message: il messaggio da inoltrare
        :return:
        """
        return self.__execute("forwardMessage", chat_id=chat_id, from_chat_id=from_chat.chat_id,
                              message_id=message.message_id)
