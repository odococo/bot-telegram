from dataclasses import dataclass

from command.general.private.private import Private
from telegram.bot import params
from telegram.ids import lampo, sara
from telegram.wrappers import Message


@dataclass
class Sara(Private):
    def can_execute(self) -> bool:
        return super().can_execute() and self.from_user().user_id == sara

    def amore(self) -> Message:
        if not params['presa'] and "presa" in self.update.message.text.lower():
            params['presa'] = True

        return self.bot.forward_message(lampo, self.update.message.chat, self.update.message)

    def tesoro(self, command: str) -> Message:
        return self.answer("Tesoro, il comando {} non l'ho ancora implementato".format(command))
