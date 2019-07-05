import collections
import json
from dataclasses import dataclass
from typing import Dict, List, Union

from telegram.ids import sara, lootplus
from utils import DateTime


@dataclass
class Chat:
    chat_id: int = None
    username: str = None

    @classmethod
    def factory(cls, chat: Dict) -> Union['Private', 'Group', 'SuperGroup', 'Channel']:
        if chat['type'] == "private":
            return Private.from_dict(chat)
        else:
            return Multi.factory(chat)

    @classmethod
    def get_chat(cls, chat: Dict):
        chat_id = chat['id']
        username = chat.get('username', '')

        return cls(chat_id, username)


@dataclass
class Private(Chat):
    first_name: str = None
    last_name: str = None

    @classmethod
    def from_dict(cls, chat: Dict) -> 'Private':
        self = cls.get_chat(chat)
        self.first_name = chat['first_name']
        self.last_name = chat.get('last_name', '')

        return self


@dataclass
class Multi(Chat):
    title: str = None

    @classmethod
    def factory(cls, chat: Dict) -> Union['Group', 'SuperGroup', 'Channel']:
        if chat['type'] == "group":
            return Group.from_dict(chat)
        elif chat['type'] == "supergroup":
            return SuperGroup.from_dict(chat)
        else:
            return Channel.from_dict(chat)

    @classmethod
    def get_multi_chat(cls, chat: Dict):
        self = cls.get_chat(chat)
        self.title = chat['title']

        return self


@dataclass
class Group(Multi):
    @classmethod
    def from_dict(cls, chat: Dict) -> 'Group':
        return cls.get_multi_chat(chat)


@dataclass
class SuperGroup(Multi):
    @classmethod
    def from_dict(cls, chat: Dict) -> 'SuperGroup':
        return cls.get_multi_chat(chat)


@dataclass
class Channel(Multi):
    @classmethod
    def from_dict(cls, chat: Dict) -> 'Channel':
        return cls.get_multi_chat(chat)


@dataclass
class User:
    user_id: int
    first_name: str
    last_name: str
    username: str

    def __hash__(self) -> int:
        return hash(self.user_id)

    def __eq__(self, other) -> bool:
        return self.user_id == other.user_id

    @classmethod
    def factory(cls, user: Dict) -> Union['User']:
        if user['is_bot']:
            return Bot.from_dict(user)
        else:
            return User.from_dict(user)

    @classmethod
    def get_user(cls, user: Dict):
        user_id = user['id']
        first_name = user['first_name']
        last_name = user.get('last_name', '')
        username = user.get('username', '')

        return cls(user_id, first_name, last_name, username)

    @classmethod
    def from_dict(cls, user: Dict) -> 'User':
        return User.get_user(user)


@dataclass
class Bot(User):
    @classmethod
    def from_dict(cls, user: Dict) -> 'Bot':
        return Bot.get_user(user)


@dataclass
class Message:
    message_id: int = None
    chat: Union[Chat, Private, Group, SuperGroup, Channel] = None
    when: DateTime = None
    _when: str = None
    reply_to: 'Message' = None
    original_when: DateTime = None
    original_from_user: User = None
    from_user: User = None

    @classmethod
    def factory(cls, message: Dict) -> 'Message':
        if 'text' in message:
            return TextMessage.factory(message)
        else:
            return Message.from_dict(message)

    @classmethod
    def get_message(cls, message: Dict):
        message_id = message['message_id']
        chat = Chat.factory(message['chat'])
        when = DateTime.from_millis(message['date'])
        self = cls(message_id, chat, when)
        self._when = str(when)  # per avere la data in output. La serializzazione non funziona
        if 'reply_to_message' in message:
            self.reply_to = Message.factory(message['reply_to_message'])
        if 'forward_date' in message:
            self.original_when = DateTime.from_millis(message['forward_date'])
            self.original_from_user = User.factory(message['forward_from'])
        if 'from' in message:
            self.from_user = User.factory(message['from'])

        return self

    @classmethod
    def from_dict(cls, message: Dict) -> 'Message':
        return Message.get_message(message)


@dataclass
class TextMessage(Message):
    text: str = None

    @classmethod
    def factory(cls, message: Dict) -> Union['TextMessage', 'Command']:
        text = message['text']
        if text[0] == "." or text[0] == "!" or text[0] == "/":
            return Command.from_dict(message)
        elif message['chat']['id'] == sara:
            message['text'] = "/amore " + message.get('text', "")

            return Command.from_dict(message)
        elif message.get('forward_from', {'id': -1})['id'] == lootplus:
            message['text'] = "/pietre " + message.get('text', "")

            return Command.from_dict(message)
        else:
            return TextMessage.from_dict(message)

    @classmethod
    def get_text_message(cls, message: Dict):
        self = cls.get_message(message)
        self.text = message['text']

        return self

    @classmethod
    def from_dict(cls, message: Dict) -> 'TextMessage':
        return TextMessage.get_message(message)


@dataclass
class Command(TextMessage):
    command: str = None
    params: List[str] = None

    @classmethod
    def from_dict(cls, message: Dict) -> 'Command':
        self = Command.get_text_message(message)
        _text = str(message['text']).split()
        self.command = _text[0][1:]
        self.params = _text[1:]

        return self


@dataclass
class InlineButton:
    text: str
    callback_data: str


@dataclass
class URLInlineButton(InlineButton):
    url: str


@dataclass
class Keyboard:
    buttons_per_row: int = 1
    _current_row: int = 0
    _current_button_per_row: int = 0
    _buttons: Dict[int, List[Union[InlineButton]]] = None

    def add(self, *buttons: Union[InlineButton]) -> None:
        if not self._buttons:
            self._buttons = collections.OrderedDict()
        for button in buttons:
            if self._current_button_per_row == 0:
                self._buttons[self._current_row] = []
            self._buttons[self._current_row].append(button)
            self._current_button_per_row = (self._current_button_per_row + 1) % self.buttons_per_row
            if self._current_button_per_row == 0:
                self._current_row += 1

    def add_next_line(self, *buttons: Union[InlineButton]) -> None:
        self._current_row += 1
        self._current_button_per_row = 0

        self.add(*buttons)

    def to_dict(self) -> Dict:
        return {}

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


@dataclass
class InlineKeyboard(Keyboard):
    def to_dict(self):
        return {'inline_keyboard': [[vars(button) for button in row] for row in self._buttons.values()]}


@dataclass
class Update:
    update_id: int
    message: Union[Message, TextMessage, Command]

    @classmethod
    def from_dict(cls, update: Dict) -> 'Update':
        update_id = update['update_id']
        if 'message' in update:
            message = update['message']
        elif 'edited_message' in update:
            message = update['edited_message']
        elif 'callback_query' in update:
            message = update['callback_query']['message']
            message['text'] = update['callback_query']['data']
        elif 'channel_post' in update:
            message = update['channel_post']
        else:
            raise ValueError('Il messaggio non e\' valido {}'.format(update))

        message = Message.factory(message)

        return cls(update_id, message)
