import json
import unicodedata as ucd

from command.general.private.private import Private
from telegram.wrappers import Message, Private as PrivateChat
from utils import join


class Standard(Private):
    def echo(self) -> Message:
        return self.answer("To you from you: {}".format(" ".join(self.params())))

    def ping(self) -> Message:
        return self.answer("pong")

    def utf(self) -> Message:
        string = " ".join(self.params())

        return self.answer(
            "\n".join(["Input: {}\nCodifica: {}\nCode point: {}\nNome: {}\nCategoria: {}".format(
                carattere, ord(carattere), json.dumps(carattere), ucd.name(carattere), ucd.category(carattere))
                for carattere in string]))

    def string(self) -> Message:
        codice = self.params()[0]

        if codice.isdigit():  # codice unicode
            return self.answer("Il carattere corrispondente a {} è {}".format(codice, chr(int(codice))))
        else:  # codifica unicode \u...
            return self.answer(
                "Il carattere corrispondente a {} è {}".format(codice, codice.encode('utf-8').decode('unicode_escape')))

    def whoami(self) -> Message:
        # TODO aggiungere parametro per cercare nel database l'utente
        user = self.from_user()

        return self.answer(
            "ID: <code>{}</code>\n"
            "First name: <code>{}</code>\n"
            "Last name: <code>{}</code>\n"
            "Username: <code>{}</code>\n"
            "<a href='tg://user?id={}'>Contattalo!</a>".format(user.user_id, user.first_name, user.last_name,
                                                               user.username, user.user_id))

    def whereami(self) -> Message:
        chat = self.from_chat()
        if isinstance(chat, PrivateChat):
            return self.answer(
                "ID: <code>{}</code>\n"
                "First name: <code>{}</code>\n"
                "Last name: <code>{}</code>\n"
                "Username: <code>{}</code>".format(chat.chat_id, chat.first_name, chat.last_name, chat.username))
        else:
            return self.answer(
                "ID: <code>{}</code>\n"
                "Title: <code>{}</code>\n"
                "Tipo: <code>{}</code>\n"
                "Username: <code>{}</code>".format(chat.chat_id, chat.title, chat.__class__, chat.username))

    def scrivi(self) -> Message:
        to = int(self.params()[0])
        text = join(self.params()[1:], " ")

        return self.send(to, text)
