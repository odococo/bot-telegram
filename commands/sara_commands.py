from dataclasses import dataclass

from commands.command import Command
from telegram.ids import lampo, sara
from telegram.wrappers import Message


@dataclass
class Sara(Command):
    def can_execute(self) -> bool:
        return self.from_user().user_id == sara

    def scrivi(self) -> Message:
        return self.bot.forward_message(lampo, self.update.message.chat, self.update.message)

    def tesoro(self, command: str) -> Message:
        return self.answer("Tesoro, il comando {} non l'ho ancora implementato".format(command))
