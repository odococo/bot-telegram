from dataclasses import dataclass
from typing import Dict

from commands.commands import Command
from telegram.ids import sara, lampo


@dataclass
class LampoCommands(Command):
    def scrivi(self) -> Dict:
        return self.bot.forward_message(sara, self.update.message.chat, self.update.message)

    def test(self) -> Dict:
        return self.bot.forward_message(lampo, self.update.message.chat, self.update.message)
