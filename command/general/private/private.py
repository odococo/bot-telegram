from dataclasses import dataclass

from command.general.general import General
from telegram.wrappers import Private as PrivateChat


@dataclass
class Private(General):
    def can_execute(self) -> bool:
        return super().can_execute() and isinstance(self.from_chat(), PrivateChat)

