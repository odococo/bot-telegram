from dataclasses import dataclass

from commands.command import Command
from telegram.ids import lampo
from telegram.wrappers import Message


@dataclass
class Sara(Command):
    def scrivi(self) -> Message:
        return self.bot.forward_message(lampo, self.update.message.chat, self.update.message)

    def tesoro(self, command: str) -> Message:
        return self.answer("Tesoro, il comando {} non l'ho ancora implementato".format(command))