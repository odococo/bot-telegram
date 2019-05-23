from dataclasses import dataclass


@dataclass
class TelegramException:
    name: str
    text: str

