from dataclasses import dataclass

from command.admin.admin import Admin
from telegram.wrappers import Group as GroupChat


@dataclass
class Group(Admin):
    def can_execute(self) -> bool:
        return super().can_execute() and isinstance(self.from_chat(), GroupChat)
