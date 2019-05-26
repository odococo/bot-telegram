from dataclasses import dataclass
from typing import Dict

from commands.command import Command
from telegram.ids import lampo


@dataclass
class SaraCommands(Command):
    def scrivi(self) -> Dict:
        return self.bot.forward_message(lampo, self.update.message.chat, self.update.message)

    def tesoro(self, command: str) -> Dict:
        return self.answer("Tesoro, il comando {} non l'ho ancora implementato".format(command))