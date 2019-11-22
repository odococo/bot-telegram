from dataclasses import dataclass

from command.general.private.private import Private
from telegram.bot import params
from telegram.ids import lampo, sara
from telegram.wrappers import Message


@dataclass
class Sara(Private):
    def can_execute(self) -> bool:
        print(super().can_execute(), super().from_user().user_id)
        return super().can_execute() and self.from_user().user_id == sara

    def amour(self) -> Message:
        if not params['presa'] and "presa" in self.update.message.text.lower():
            params['presa'] = True
            return self.answer("\ufe0f")

        return self.bot.forward_message(lampo, self.update.message.chat, self.update.message)

    def tesoro(self, command: str) -> Message:
        return self.answer("Tesoro, il comando {} non l'ho ancora implementato".format(command))
