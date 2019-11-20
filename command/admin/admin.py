from dataclasses import dataclass

from command.command import Command
from telegram.ids import lampo


@dataclass
class Admin(Command):
    def can_execute(self) -> bool:
        return super().can_execute() and self.from_user().user_id == lampo
