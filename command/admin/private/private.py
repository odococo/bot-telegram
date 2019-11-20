from dataclasses import dataclass

from command.admin.admin import Admin
from telegram.wrappers import Private as PrivateChat


@dataclass
class Private(Admin):
    def can_execute(self) -> bool:
        return super().can_execute() and isinstance(self.from_chat(), PrivateChat)
