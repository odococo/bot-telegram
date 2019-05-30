import collections
import json
from dataclasses import dataclass
from typing import Dict, List, Union

from telegram.ids import sara, lootplus
from utils import Date


@dataclass
class Chat:
    chat_id: int
    username: str

    @classmethod
    def from_dict(cls, chat: Dict) -> 'Chat':
        if chat['type'] == "private":
            return PrivateChat.from_dict(chat)
        elif chat['type'] == 'group' or chat['type'] == 'supergroup':
            return GroupChat.from_dict(chat)
        else:
            chat_id = chat['id']
            username = chat.get('username', '')

            return cls(chat_id, username)


@dataclass
class PrivateChat(Chat):
    first_name: str
    last_name: str

    @classmethod
    def from_dict(cls, chat: Dict) -> 'PrivateChat':
        chat_id = chat['id']
        first_name = chat['first_name']
        last_name = chat.get('last_name', '')
        username = chat.get('username', '')

        return cls(chat_id, first_name, last_name, username)


@dataclass
class GroupChat(Chat):
    title: str
    supergroup: bool

    @classmethod
    def from_dict(cls, chat: Dict) -> 'GroupChat':
        chat_id = chat['id']
        title = chat['title']
        supergroup = chat['type'] == "supergroup"
        username = chat.get('username', '')

        return cls(chat_id, title, supergroup, username)


@dataclass
class User:
    user_id: int
    first_name: str
    last_name: str
    username: str

    @classmethod
    def from_dict(cls, user: Dict) -> 'User':
        user_id = user['id']
        first_name = user['first_name']
        last_name = user.get('last_name', '')
        username = user.get('username', '')

        return cls(user_id, first_name, last_name, username)


@dataclass
class Message:
    message_id: int
    chat: Union[Chat, PrivateChat, GroupChat]
    when: Date
    from_user: User
    reply_to: 'Message'
    original_when: Date
    original_from_user: User

    @classmethod
    def from_dict(cls, message: Dict) -> 'Message':
        if 'text' in message:
            text = message['text']
            if text[0] == "." or text[0] == "!" or text[0] == "/":
                return Command.from_dict(message)
            else:
                return TextMessage.from_dict(message)
        else:
            message_id = message['message_id']
            chat = Chat.from_dict(message['chat'])
            when = Date.from_millis(message['date'])
            from_user = User.from_dict(message['from'])
            if 'reply_to_message' in message:
                reply_to = Message.from_dict(message['reply_to_message'])
            else:
                reply_to = None
            if 'forward_date' in message:
                original_when = Date.from_millis(message['forward_date'])
                original_from_user = User.from_dict(message['forward_from'])
            else:
                original_when = None
                original_from_user = None

            return cls(message_id, chat, when, from_user, reply_to, original_when, original_from_user)


@dataclass
class TextMessage(Message):
    text: str

    @classmethod
    def from_dict(cls, message: Dict) -> 'TextMessage':
        message_id = message['message_id']
        chat = Chat.from_dict(message['chat'])
        when = Date.from_millis(message['date'])
        from_user = User.from_dict(message['from'])
        text = message['text']
        if 'reply_to_message' in message:
            reply_to = Message.from_dict(message['reply_to_message'])
        else:
            reply_to = None
        if 'forward_date' in message:
            original_when = Date.from_millis(message['forward_date'])
            original_from_user = User.from_dict(message['forward_from'])
        else:
            original_when = None
            original_from_user = None

        return cls(message_id, chat, when, from_user, reply_to, original_when, original_from_user, text)


@dataclass
class Command(TextMessage):
    command: str
    params: List[str]

    @classmethod
    def from_dict(cls, message: Dict) -> 'Command':
        message_id = message['message_id']
        chat = Chat.from_dict(message['chat'])
        when = Date.from_millis(message['date'])
        from_user = User.from_dict(message['from'])
        if 'reply_to_message' in message:
            reply_to = Message.from_dict(message['reply_to_message'])
        else:
            reply_to = None
        if 'forward_date' in message:
            original_when = Date.from_millis(message['forward_date'])
            original_from_user = User.from_dict(message['forward_from'])
        else:
            original_when = None
            original_from_user = None
        text = message['text']
        _text = str(message['text']).split(" ")
        command = _text[0][1:]
        params = _text[1:]

        return cls(message_id, chat, when, from_user, reply_to, original_when, original_from_user, text, command,
                   params)


@dataclass
class InlineButton:
    text: str
    callback_data: str


@dataclass
class URLInlineButton(InlineButton):
    url: str


@dataclass
class Keyboard:
    buttons: Dict[int, List[Union[InlineButton]]] = None

    def add(self, row: int, *buttons: Union[InlineButton]):
        if not self.buttons:
            self.buttons = collections.OrderedDict()
        self.buttons.setdefault(row, [])
        self.buttons[row] += buttons

    def to_dict(self) -> Dict:
        return {}

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


@dataclass
class InlineKeyboard(Keyboard):
    def to_dict(self):
        return {'inline_keyboard': [[vars(button) for button in row] for row in self.buttons.values()]}


@dataclass
class Update:
    update: Dict
    update_id: int
    message: Union[Message, TextMessage, Command]

    @classmethod
    def from_dict(cls, update: Dict) -> 'Update':
        print(update)
        update_id = update['update_id']
        if 'message' in update:
            message = update['message']
        elif 'edited_message' in update:
            message = update['edited_message']
        elif 'callback_query' in update:
            message = update['callback_query']['message']
            message['text'] = update['callback_query']['data']
        else:
            raise ValueError('Il messaggio non e\' valido {}'.format(update))

        if message['chat']['id'] == sara:
            message['text'] = "/scrivi " + message.get('text', "")
        elif message.get('forward_from', {'id': -1})['id'] == lootplus:
            message['text'] = "/pietre " + message.get('text', "")

        message = Message.from_dict(message)

        return cls(update, update_id, message)
