from dataclasses import dataclass

from commands.commands import Command
from telegram.wrappers import Message


@dataclass
class Loot(Command):
    def pietre(self) -> Message:
        valori_pietre = {
            'Pietra Anima di Legno': 1,
            'Pietra Anima di Ferro': 2,
            'Pietra Anima Preziosa': 3,
            'Pietra Cuore di Diamante': 4,
            'Pietra Cuore Leggendario': 5,
            'Pietra Spirito Epico': 6
        }
        quantita_pietre = list(
            filter(lambda string: string.startswith("> Pietra"), self.update.message.text.split("\n")))
        valore_per_pietra = ["Valore delle pietre"]
        totale = 0
        for pietra in quantita_pietre:
            tipo = pietra[pietra.index("Pietra"):pietra.index("(") - 1]
            quantita = pietra[pietra.index(",") + 2:pietra.index(")")]
            tot = int(quantita.replace(".", "")) * valori_pietre[tipo]
            valore_per_pietra.append("{}: {} punti".format(tipo, tot))
            totale += tot
        valore_per_pietra.append("Totale: {} ==> {} livelli".format(totale, totale // 70))

        return self.answer("\n".join(valore_per_pietra))
