import unicodedata
from dataclasses import dataclass

import requests

from commands.commands import Command
from sara_commands import presa
from telegram.ids import sara, lampo
from telegram.wrappers import Message
from utils import DateTime

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
    'ata duan': "loro vogliono",
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
class Lampo(Command):
    def can_execute(self) -> bool:
        return self.from_user().user_id == lampo

    def scrivi(self) -> Message:
        return self.bot.forward_message(sara, self.update.message.chat, self.update.message)

    def ricorda(self) -> Message:
        if presa:
            return self.answer("Sembra l'abbia presa")
        else:
            return self.bot.send_message(chat_id=sara, text="Saraaaaaaaaaaaaaa non dimenticartelaaaaaaaaaaaaaaa")

    def test(self) -> Message:
        return self.bot.forward_message(lampo, self.update.message.chat, self.update.message)

    def traduci(self) -> Message:
        lingua = self.params()[0]
        parola = " ".join(self.params()[1:])

        if lingua == "it":
            parole = ["<strong>{}</strong> --> <code>{}</code>".format(it, al) for al, it in traduzioni.items() if
                      parola in it]
        else:
            parole = ["<strong>{}</strong> --> <code>{}</code>".format(al, it) for al, it in traduzioni.items() if
                      parola in al or parola in str(unicodedata.normalize('NFKD', al).encode('ascii', 'ignore'))]

        if len(parole):
            return self.answer("Le traduzioni che contengono {} sono: \n{}".format(parola, "\n".join(parole)))
        else:
            return self.answer("Non ci sono traduzioni per {}".format(parola))

    def whatismyip(self) -> Message:
        return self.bot.debug(ip=requests.get("http://ipinfo.io?").json())

    def server_time(self):
        return self.answer(str(DateTime.by_now()))

    def getavvisi(self):
        return self.answer("\n".join(
            ["id: <code>{}</code> ==> {}".format(job.id, job.next_run_time) for job in self.bot.scheduler.get_jobs()]))
