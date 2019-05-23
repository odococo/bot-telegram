from dataclasses import dataclass
from typing import Dict

from telegram.bot import Bot
from telegram.wrappers import Update


def execute(bot, update):
    command = update.message.command
    default = Command(bot, update)
    standard = Standard(bot, update)
    lampo = LampoCommands(bot, update)
    sara = SaraCommands(bot, update)
    if hasattr(standard, command):
        getattr(standard, command)()
    elif update.message.from_user.user_id == bot.sara:
        if hasattr(sara, command):
            getattr(sara, command)()
        else:
            getattr(sara, "tesoro")(command)
    elif update.message.from_user.user_id == bot.lampo:
        if hasattr(lampo, command):
            getattr(lampo, command)()
        else:
            getattr(default, "error")(command)
    else:
        getattr(default, "error")(command)


@dataclass
class Command:
    bot: Bot
    update: Update

    def answer(self, text: str) -> Dict:
        """
        Risponde all'utente che ha eseguito il comando

        :param text: testo di risposta
        :return:
        """
        return self.bot.send_message(chat_id=self.update.message.chat.chat_id, text=text,
                                     reply_to=self.update.message.message_id)

    def error(self, command: str) -> Dict:
        return self.answer("Il comando {} non esiste!".format(command))


@dataclass
class SaraCommands(Command):
    def scrivi(self) -> Dict:
        return self.bot.forward_message(self.bot.lampo, self.update.message.chat, self.update.message)

    def tesoro(self, command: str) -> Dict:
        return self.answer("Tesoro, il comando {} non l'ho ancora implementato".format(command))


@dataclass
class LampoCommands(Command):
    def scrivi(self):
        return self.bot.forward_message(self.bot.sara, self.update.message.chat, self.update.message)


@dataclass
class Standard(Command):
    def echo(self):
        return self.answer("To you from you: " + " ".join(self.update.message.params))
