import json
import random
import unicodedata as ucd
from dataclasses import dataclass

from commands import command as c
from commands.commands import Command
from telegram.wrappers import InlineKeyboard, InlineButton, Message, Private
from utils import join


@dataclass
class Standard(Command):
    def can_execute(self) -> bool:
        return True

    def echo(self) -> Message:
        return self.answer("To you from you: {}".format(" ".join(self.params())))

    def random(self) -> Message:
        """
        Estrae 1 numero random tra min (intero) e max (intero

        Sintassi: /random min max [X]
        """
        min_value = int(self.params()[0])
        max_value = int(self.params()[1])

        return self.answer(str(random.randint(min_value, max_value)))

    def roll(self) -> Message:
        if not len(self.params()):
            text = "Specifica il numero di facce:"
            keyboard = InlineKeyboard(3)
            keyboard.add(
                InlineButton("6", "/{} 6".format(self.command())),
                InlineButton("10", "/{} 10".format(self.command())),
                InlineButton("20", "/{} 20".format(self.command())),
                InlineButton("50", "/{} 50".format(self.command())),
                InlineButton("100", "/{} 100".format(self.command())),
                InlineButton("1000", "/{} 1000".format(self.command()))
            )

            return self.answer(text, keyboard)
        elif len(self.params()) == 1:
            facce = int(self.params()[0])
            text = "Specifica il numero di lanci:"
            keyboard = InlineKeyboard(3)
            keyboard.add(
                InlineButton("1", "/{} {} 1".format(self.command(), facce)),
                InlineButton("2", "/{} {} 2".format(self.command(), facce)),
                InlineButton("3", "/{} {} 3".format(self.command(), facce)),
                InlineButton("4", "/{} {} 4".format(self.command(), facce)),
                InlineButton("5", "/{} {} 5".format(self.command(), facce)),
                InlineButton("6", "/{} {} 6".format(self.command(), facce)),
                InlineButton("7", "/{} {} 7".format(self.command(), facce)),
                InlineButton("8", "/{} {} 8".format(self.command(), facce)),
                InlineButton("9", "/{} {} 9".format(self.command(), facce))
            )

            return self.replace(text, keyboard)
        else:
            facce = int(self.params()[0])
            lanci = int(self.params()[1])
            text = "Dado a {} facce\n".format(facce)
            text += "\n".join(["Lancio {} di {}: {}".format(i + 1, lanci, lancio) for i, lancio in
                               enumerate(random.choices(range(1, facce), k=lanci))])

            return self.replace(text)

    def utf(self) -> Message:
        string = " ".join(self.params())

        return self.answer(
            "\n".join(["Input: {}\nCodifica: {}\nCode point: {}\nNome: {}\nCategoria: {}".format(
                carattere, ord(carattere), json.dumps(carattere), ucd.name(carattere), ucd.category(carattere))
                for carattere in string]))

    def string(self) -> Message:
        codice = self.params()[0]

        if codice.isdigit():  # codice unicode
            return self.answer("Il carattere corrispondente a {} è {}".format(codice, chr(int(codice))))
        else:  # codifica unicode \u...
            return self.answer(
                "Il carattere corrispondente a {} è {}".format(codice, codice.encode('utf-8').decode('unicode_escape')))

    def whoami(self) -> Message:
        # TODO aggiungere parametro per cercare nel database l'utente
        user = self.from_user()

        return self.answer(
            "ID: <code>{}</code>\n"
            "First name: <code>{}</code>\n"
            "Last name: <code>{}</code>\n"
            "Username: <code>{}</code>\n"
            "<a href='tg://user?id={}'>Contattalo!</a>".format(user.user_id, user.first_name, user.last_name,
                                                               user.username, user.user_id))

    def whereami(self) -> Message:
        chat = self.update.message.chat
        if isinstance(chat, Private):
            return self.answer(
                "ID: <code>{}</code>\n"
                "First name: <code>{}</code>\n"
                "Last name: <code>{}</code>\n"
                "Username: <code>{}</code>".format(chat.chat_id, chat.first_name, chat.last_name, chat.username))
        else:
            return self.answer(
                "ID: <code>{}</code>\n"
                "Title: <code>{}</code>\n"
                "Tipo: <code>{}</code>\n"
                "Username: <code>{}</code>".format(chat.chat_id, chat.title, chat.__class__, chat.username))

    def scrivi(self) -> Message:
        to = int(self.params()[0])
        text = join(self.params()[1:], " ")

        return self.send(to, text)

    def help(self) -> Message:
        if not self.params():
            keyboard = InlineKeyboard(2)
            for command_type in c.get_commands_list(self.bot, self.update):
                if command_type.can_execute():
                    name = type(command_type).__name__
                    keyboard.add(InlineButton("{}".format(name), "/{} {}".format(self.command(), name)))

            return self.answer("Ecco le categorie di comandi disponibili", keyboard)
        elif len(self.params()) == 1:
            command_type = c.get_command_instance(self.params()[0], self.bot, self.update)
            keyboard = InlineKeyboard(2)
            for command in command_type.get_commands():
                keyboard.add(InlineButton("{}".format(command),
                                          "/{} {} {}".format(self.command(), join(self.params(), " "), command)))

            return self.replace("Ecco i comandi disponbili per {}".format(self.params()[0]), keyboard)
        else:
            return self.replace(
                "Il comando è /{}\n\nPer consultare la documentazion: <code>/doc {}</code>".format(self.params()[1],
                                                                                                   self.params()[1]))

    def doc(self) -> Message:
        command = self.params()[0]
        documentazione = c.get_command(self.bot, self.update, command).__doc__

        return self.answer("Comando: /{}\nDocumentazione: {}".format(command, documentazione))
