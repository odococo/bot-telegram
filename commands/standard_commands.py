import random
from dataclasses import dataclass
from typing import Dict

from commands.commands import Command
from telegram.wrappers import InlineKeyboard, InlineButton


@dataclass
class Standard(Command):
    def echo(self) -> Dict:
        return self.answer("To you from you: " + " ".join(self.update.message.params))

    def random(self) -> Dict:
        """
        Estrae 1 numero random tra min (intero) e max (intero

        Sintassi: /random min max [X]
        """
        min_value = int(self.params()[0])
        max_value = int(self.params()[1])

        return self.answer(str(random.randint(min_value, max_value)))

    def roll(self) -> Dict:
        if not len(self.params()):
            text = "Specifica il numero di facce:"
            keyboard = InlineKeyboard()
            keyboard.add(1, InlineButton("6", "/roll 6"), InlineButton("10", "/roll 10"),
                         InlineButton("20", "/roll 20"))
            keyboard.add(2, InlineButton("50", "/roll 50"), InlineButton("100", "/roll 100"),
                         InlineButton("1000", "/roll 1000"))

            return self.answer(text, keyboard)
        elif len(self.params()) == 1:
            facce = int(self.params()[0])
            text = "Specifica il numero di lanci:"
            keyboard = InlineKeyboard()
            keyboard.add(1, InlineButton("1", "/roll {} 1".format(facce)),
                         InlineButton("2", "/roll {} 2".format(facce)), InlineButton("3", "/roll {} 3".format(facce)))
            keyboard.add(2, InlineButton("4", "/roll {} 4".format(facce)),
                         InlineButton("5", "/roll {} 5".format(facce)),
                         InlineButton("6", "/roll {} 6".format(facce)))
            keyboard.add(3, InlineButton("7", "/roll {} 7".format(facce)),
                         InlineButton("8", "/roll {} 8".format(facce)), InlineButton("9", "/roll {} 9".format(facce)))

            return self.replace(text, keyboard)
        else:
            facce = int(self.params()[0])
            lanci = int(self.params()[1])
            text = "Dado a {} facce\n".format(facce)
            text += "\n".join(["Lancio {} di {}: {}".format(i + 1, lanci, lancio) for i, lancio in
                               enumerate(random.choices(range(1, facce), k=lanci))])

            return self.replace(text)
