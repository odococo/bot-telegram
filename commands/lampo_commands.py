import unicodedata
from dataclasses import dataclass
from typing import Dict

from commands.commands import Command
from telegram.ids import sara, lampo

traduzioni = {
    'çfarë dreqin po thua': "che diavolo stai dicendo",

    'faleminderit': "grazie",
    'nuk ka gje': "prego formale",
    'ska gje': "prego",

    'natën': "notte",
    'natën e mir': "buonanotte",
    'mirëdita': "buongiorno",
    'çkemi': "ciao",
    'përshëndetje': "salve",

    'si je?': "come stai?",
    'mir': "bene",
    'keq': "male",
    'jo': "no",
    'po': "sì",

    'si': "come",

    'te dua': "ti amo",
    'shpirt': "tesoro",
    'zëmre': "amore",

    'dua gjumë': "voglio sonno",
    'uri': "fame",
    'caldo': "vapa",
    'ftoht': "freddo",

    'un': "io",
    'ti': "tu",
    'aji': "lui",
    'ajo': "lei",
    'neve': "noi",
    'juve': "voi",
    'ata': "loro",
    'un kam': "io ho",
    'ti ke': "tu hai",
    'aji ka': "lui ha",
    'ajo ka': "lei ha",
    'neve kemi': "noi abbiamo",
    'juve keni': "voi avete",
    'ata kan': "loro hanno",
    'un dua': "io voglio",
    'ti do': "tu vuoi",
    'aji do': "lui vuole",
    'ajo do': "lei vuole",
    'neve duam': "noi vogliamo",
    'juve doni': "voi volete",
    'ata duan': "loro vogliono'",
    'un jam': "io sono",
    'ti je': "tu sei",
    'aji është': "lui è",
    'ajo është': "lei è",
    'neve jemi': "noi siamo",
    'juve jeni': "voi siete",
    'ata jan': "loro sono",

    'zero': "zero",
    'nje': "uno",
    'dy': "due",
    'tre': "tre",
    'katër': "quattro",
    'pes': "cinque",
    'gjasht': "sei",
    'shtat': "sette",
    'tet': "otto",
    'nënt': "nove"
}


@dataclass
class LampoCommands(Command):
    def scrivi(self) -> Dict:
        return self.bot.forward_message(sara, self.update.message.chat, self.update.message)

    def test(self) -> Dict:
        return self.bot.forward_message(lampo, self.update.message.chat, self.update.message)

    def traduci(self) -> Dict:
        lingua = self.params()[0]
        parola = " ".join(self.params()[1:])

        if lingua == "it":
            parole = ["<strong>{}</strong> --> <code>{}</code>".format(it, al) for al, it in traduzioni.items() if parola in it]
        else:
            parole = ["<strong>{}</strong> --> <code>{}</code>".format(al, it) for al, it in traduzioni.items() if
                      parola in al or parola in str(unicodedata.normalize('NFKD', al).encode('ascii', 'ignore'))]

        if len(parole):
            return self.answer("Le traduzioni che contengono {} sono: \n{}".format(parola, "\n".join(parole)))
        else:
            return self.answer("Non ci sono traduzioni per {}".format(parola))
