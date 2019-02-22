from dataclasses import dataclass
from typing import List

from Utils.TimeUtils import Date
from Wrappers.ChatType import Chat
from Wrappers.EntityType import Entity
from Wrappers.FileType import File
from Wrappers.UserType import User


@dataclass
class Type:
    pass


@dataclass
class Message:
    id: int
    from_user: User
    date: Date
    chat: Chat
    type: Type


@dataclass
class Direct(Type):
    pass


@dataclass
class Forward(Type):
    original_user: User
    original_date: Date


@dataclass
class Reply(Type):
    to: Message


@dataclass
class Text(Message):
    text: str
    entities: List[Entity]


@dataclass
class Files:
    file: List[File]
