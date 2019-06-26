from dataclasses import dataclass
from typing import List, Dict, Callable

from telegram.bot import Bot
from telegram.ids import lampo
from telegram.wrappers import Update, Keyboard, Message, User


@dataclass
class Command:
    bot: Bot
    update: Update

    def can_execute(self) -> bool:
        return False

    def get_commands(self) -> List[str]:
        return [
            command for command in dir(self)
            if not command.startswith("_") and not command.startswith("can") and callable(
                getattr(self, command)) and command in type(self).__dict__
        ]

    def command(self):
        return self.update.message.command

    def params(self) -> List[str]:
        return self.update.message.params

    def from_user(self) -> User:
        if self.update.message.reply_to:
            return self.update.message.reply_to.from_user
        else:
            return self.update.message.from_user

    def answer(self, text: str, keyboard: Keyboard = Keyboard()) -> Message:
        """
        Risponde all'utente che ha eseguito il comando

        :param text: testo di risposta
        :param keyboard: eventuale tastiera
        :return:
        """
        return self.bot.send_message(chat_id=self.update.message.chat.chat_id, text=text,
                                     reply_to=self.update.message.message_id, keyboard=keyboard)

    def replace(self, text: str, keyboard: Keyboard = Keyboard()) -> Message:
        """
        Rimpiazza il precedente messaggio

        :param text: il nuovo testo di risposta
        :param keyboard: la nuova eventuale tastiera
        :return:
        """
        return self.bot.edit_message(chat_id=self.update.message.chat.chat_id,
                                     message_id=self.update.message.message_id,
                                     text=text, keyboard=keyboard)

    def error(self) -> Message:
        return self.answer("Il comando {} non esiste!".format(self.command()))

    def unauthorized(self) -> Message:
        """Non sei autorizzato ad usare questo comando né a conoscere i dettagli del suo utilizzo"""

        return self.answer("Non sei autorizzato ad usare questo comando né a conoscere i dettagli del suo utilizzo!")

    def wrong(self, command: Callable[[], Dict]) -> Message:
        if not command.__doc__:
            self.bot.send_message(chat_id=lampo, text="Il comando {} non ha una doc!".format(command.__name__))

        return self.answer(
            "Hai usato male il comando {}. Le istruzioni per il comando sono:\n\n {}".format(command.__name__,
                                                                                             command.__doc__))
