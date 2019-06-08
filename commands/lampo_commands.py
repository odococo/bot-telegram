import unicodedata
from dataclasses import dataclass
from typing import Dict

from commands.commands import Command
from telegram.ids import sara, lampo

traduzioni = {
    'nuk ka gje': "prego formale",
    'natën': "notte",
    'natën mir': "buonanotte",
    'faleminderit': "grazie",
    'ska gje': "prego",
    'çfarë dreqin po thua': "che diavolo stai dicendo",
    'çkemi': "ciao",
    'mir': "bene",
    'keq': "male",
    'jo': "no",
    'po': "sì",
    'te dua': "ti amo",
    'mirëdita': "buongiorno"
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
