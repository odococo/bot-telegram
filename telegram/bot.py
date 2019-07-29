import datetime
import logging
from typing import Dict, List, Union

import jsonpickle
import requests
from apscheduler.schedulers.background import BackgroundScheduler

from telegram.ids import lampo
from telegram.wrappers import Update, Chat, Message, Keyboard

jsonpickle.set_encoder_options('json', sort_keys=True, indent=4)

max_length = 2048

params = {
    'presa': True
}


class Bot:
    url = "https://api.telegram.org/bot{token}/{method}"
    scheduler: BackgroundScheduler = None
    last_exception = None

    #  scheduler = BackgroundScheduler(timezone=utc)

    def __init__(self, token: str):
        self.token = token
        if self.scheduler is None:
            self.scheduler = BackgroundScheduler()
        self.scheduler.start()

    def __execute(self, method: str, **parametri) -> Dict:
        """
        Esegue una httprequest con il metodo

        :param method: nome del metodo da eseguire
        :param params: parametri del metodo da eseguire
        :return: il contenuto della risposta oppure l'errore
        """
        request = requests.get(self.url.format(token=self.token, method=method), params=parametri)
        if request.ok:
            return request.json()['result']
        else:
            logging.warning(request.json())
            error = request.json().get('error', request.json().get('description', request.json()))
            self.last_exception = error
            logging.warning(error)
            if error != "Bad Request: message to delete not found":
                pass
                # raise Exception(error)

    def add_cron_job(self, function: callable, single: bool,
                     time_details: Dict[str, Union[int, datetime.datetime]]) -> str:
        job_id = self.scheduler.add_job(func=function, trigger='date' if single else 'interval', **time_details).id
        logging.info("Aggiunto job con id {}".format(job_id))
        logging.info("{}".format(self.scheduler.get_job(job_id)))

        return job_id

    def remove_cron_job(self, job_id: str):
        logging.info("Rimosso job con id {}".format(job_id))
        self.scheduler.remove_job(job_id)

    def dump(self, to: int, *args, **kwargs) -> Message:
        return self.send_message(to, jsonpickle.encode(args, unpicklable=False) + "\n" +
                                 jsonpickle.encode(kwargs, unpicklable=False))

    def debug(self, *args, **kwargs) -> Message:
        return self.dump(lampo, *args, **kwargs)

    def get_updates(self, last_update=0) -> List[Update]:
        """
        Cerca se ci sono stati update dall'ultima volta che sono stati controllati

        :param last_update: id dell'ultimo update
        :return: la lista, eventualmente vuota, di update
        """
        updates = self.__execute("getUpdates", offset=last_update)

        return [Update.from_dict(update) for update in updates]

    def send_message(self, chat_id: int, text: str, parse_mode: str = "HTML", reply_to: int = None,
                     keyboard: Keyboard = Keyboard()) -> Message:
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
        try:
            while len(text) > max_length:  # lunghezza massima è 2*max
                index = text.find("\n", max_length)  # se il messaggio troppo lungo errore oppure perde markup
                result = Message.factory(
                    self.__execute("sendMessage", chat_id=chat_id, text=text[:index],
                                   parse_mode=parse_mode, reply_to_message_id=reply_to))
                text = text[index:]
                reply_to = result.message_id if result.message_id else None

            return Message.factory(
                self.__execute("sendMessage", chat_id=chat_id, text=text,
                               parse_mode=parse_mode, reply_to_message_id=reply_to, reply_markup=keyboard.to_json()))
        except KeyError:
            #  non esiste messaggio a cui fare reply
            return self.send_message(chat_id=chat_id, text=text, parse_mode=parse_mode, keyboard=keyboard)

    def edit_message(self, chat_id: int, message_id: int, text: str, parse_mode: str = "HTML",
                     keyboard: Keyboard = Keyboard()) -> Message:
        """
        Edita un messaggio precedentemente inviato

        :param chat_id: chat dov'è presente il messaggio
        :param message_id: id del messaggio da modificare
        :param text: il nuovo testo del messaggio
        :param parse_mode: Markdown o HTML
        :param keyboard: la nuova tastiera da mostrare eventualmente
        :return:
        """
        try:
            result = Message.factory(self.__execute("editMessageText", chat_id=chat_id, message_id=message_id,
                                                    text=text[:max_length], parse_mode=parse_mode,
                                                    reply_markup=keyboard.to_json()))
            if len(text) > max_length:
                return self.send_message(chat_id=chat_id, text=text[max_length:], parse_mode=parse_mode,
                                         reply_to=result.message_id)

            return result
        except KeyError:
            return self.send_message(chat_id=chat_id, text=text, parse_mode=parse_mode, keyboard=keyboard)

    def forward_message(self, chat_id: int, from_chat: Chat, message: Message) -> Message:
        """
        Inoltra un messaggio

        :param chat_id: a chi inoltrare il messaggio
        :param from_chat: da dove arriva il messaggio
        :param message: il messaggio da inoltrare
        :return:
        """
        return Message.factory(self.__execute("forwardMessage", chat_id=chat_id, from_chat_id=from_chat.chat_id,
                                              message_id=message.message_id))

    def delete_message(self, chat_id: int, message_id: int) -> Union[bool, None]:
        """
        Cancella un messaggio

        :param chat_id: chat dov'è presente il messaggio da cancellare
        :param message_id: id del messaggio da cancellare
        """
        result = self.__execute("deleteMessage", chat_id=chat_id, message_id=message_id)
        if bool(result):
            return True
        else:
            if self.last_exception == "Bad Request: message can't be deleted":
                return None
            else:
                return False
