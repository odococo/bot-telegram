import unicodedata
from dataclasses import dataclass
from typing import Dict

from commands.commands import Command
from telegram.ids import sara, lampo

traduzioni = {
    'nuk ka gje': "prego formale",
    'natën': "notte",
    'faleminderit': "grazie",
    'ska gje': "prego",
    'çfarë dreqesh po thua': "che diavolo stai dicendo",
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
            parole = ["{} --> <code>{}</code>".format(it, al) for al, it in traduzioni.items() if parola in it]
        else:
            parole = ["{} --> {}".format(al, it) for al, it in traduzioni.items() if
                      parola in al or parola in str(unicodedata.normalize('NFKD', al).encode('ascii', 'ignore'))]

        return self.answer("Le traduzioni che contengono {} sono: \n{}".format(parola, "\n".join(parole)))
