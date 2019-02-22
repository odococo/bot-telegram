from dataclasses import dataclass


@dataclass
class Entity:
    value: str


@dataclass
class Mention(Entity):
    pass


@dataclass
class HashTag(Entity):
    pass


@dataclass
class Command(Entity):
    pass


@dataclass
class Url(Entity):
    pass
