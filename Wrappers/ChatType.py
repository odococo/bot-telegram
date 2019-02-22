from dataclasses import dataclass

from Wrappers.UserType import User


@dataclass
class Chat:
    id: int


@dataclass
class Private(Chat):
    user: User


@dataclass
class _MultiUser:
    title: str


@dataclass
class Group(_MultiUser):
    pass


@dataclass
class SuperGroup(_MultiUser):
    pass


@dataclass
class Channel(_MultiUser):
    pass
