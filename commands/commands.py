import time
from dataclasses import dataclass
from typing import List, Dict, Callable

from telegram.bot import Bot
from telegram.ids import lampo
from telegram.wrappers import Update, Keyboard


@dataclass
class Command:
    bot: Bot
    update: Update

    def command(self):
        return self.update.message.command

    def params(self) -> List[str]:
        return self.update.message.params

    def answer(self, text: str, keyboard: Keyboard = Keyboard()) -> Dict:
        """
        Risponde all'utente che ha eseguito il comando

        :param text: testo di risposta
        :param keyboard: eventuale tastiera
        :return:
        """
        return self.bot.send_message(chat_id=self.update.message.chat.chat_id, text=text,
                                     reply_to=self.update.message.message_id, keyboard=keyboard)

    def replace(self, text: str, keyboard: Keyboard = Keyboard()) -> Dict:
        """
        Rimpiazza il precedente messaggio

        :param text: il nuovo testo di risposta
        :param keyboard: la nuova eventuale tastiera
        :return:
        """
        result = self.bot.edit_message(chat_id=self.update.message.chat.chat_id,
                                       message_id=self.update.message.message_id,
                                       text=text, keyboard=keyboard)
        return result if result else self.answer(text, keyboard)

    def error(self, command: str) -> Dict:
        return self.answer("Il comando {} non esiste!".format(command))

    def wrong(self, command: Callable[[], Dict]) -> Dict:
        if not command.__doc__:
            self.bot.send_message(chat_id=lampo, text="Il comando {} non ha una doc!".format(command.__name__))
        return self.answer(
            "Hai usato male il comando {}. Le istruzioni per il comando sono:\n\n {}".format(command.__name__,
                                                                                             command.__doc__))
