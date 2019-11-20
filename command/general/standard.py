import random

from command.general.general import General
import telegram.executor as exe
from telegram.wrappers import Message, InlineKeyboard, InlineButton


class Standard(General):
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

    def help(self) -> Message:
        """if not self.params():
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
                                                                                                   self.params()[1]))"""
        pass

    def doc(self) -> Message:
        """command = self.params()[0]
        documentazione = c.get_command(self.bot, self.update, command).__doc__

        return self.answer("Comando: /{}\nDocumentazione: {}".format(command, documentazione))"""
        pass
