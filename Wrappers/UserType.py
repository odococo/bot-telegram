from dataclasses import dataclass


@dataclass
class User:
    id: int
    username: str
    first_name: str = None
    last_name: str = None
    lang: str = None


@dataclass
class Human(User):
    pass


@dataclass
class Bot(User):
    pass
