from dataclasses import dataclass
from typing import Dict, List

import bs4
import logging

from commands.commands import Command
from telegram.wrappers import InlineKeyboard, InlineButton, Message
from utils import WebScraper, Date, Time, chunks, DateTime

edifici: Dict = {}

tries = 1


@dataclass
class _Lezione:
    start: Time
    end: Time
    facolta: str
    dettagli: str
    corso: str

    def __eq__(self, other):
        return isinstance(other, _Lezione) and self.corso == other.corso

    def __hash__(self):
        return hash(self.corso)


def _get_aula(aula: bs4.element.Tag) -> Dict[str, List[_Lezione]]:
    lezioni = [lezione.find('div') for lezione in
               aula.find_all('td', {'class': "filled"})]  # trovo tutte le aule in cui c'e' una lezione
    nome_aula = lezioni[0].text
    aula = {
        'nome': nome_aula,
        'lezioni': []
    }
    for i in range(1, len(lezioni)):
        params = lezioni[i].find_all('div')
        ora = params[1].text.split(" - ")
        facolta = params[2].text
        dettagli = params[3].text
        corso = params[4].text if len(params) > 4 else ""

        lezione = _Lezione(Time.from_string(ora[0]), Time.from_string(ora[1]), facolta, dettagli, corso)
        aula['lezioni'].append(lezione)

    return aula


def get_timeline(edificio) -> bool:
    global tries

    if edificio not in edifici or edifici[edificio]['data'].day != Date.by_now().day:
        logging.info("web scraping per {} con {} secondo/i di attesa".format(edificio, tries))
        url = "http://timeline.uninsubria.it/browse.php?sede={}"

        scraper = WebScraper.firefox()
        timeline = scraper.get_page(url.format(edificio), tries)

        aule = []
        aule_edificio = timeline.find_all('tr')
        for i in range(1, len(aule_edificio)):
            aule.append(_get_aula(aule_edificio[i]))

        if len(aule) > 0:
            edifici[edificio] = {
                'data': Date.by_now(),
                'aule': aule  # lista di aule
            }
            tries = 1
        else:
            tries += 1

            return False
        scraper.quit()

    return True


@dataclass
class Insubria(Command):
    driver = None

    def aule(self) -> Message:
        if not len(self.params()):
            keyboard = InlineKeyboard()
            keyboard.add(1, InlineButton("Monte generoso", "/{} mtg".format(self.command())))
            keyboard.add(2, InlineButton("Morselli", "/{} mrs".format(self.command())))
            keyboard.add(3, InlineButton("Seppilli", "/{} sep".format(self.command())))

            return self.answer("Scegli l'edificio:", keyboard)
        elif len(self.params()) == 1:
            edificio = self.params()[0]
            now = Time.now()
            keyboard = InlineKeyboard()
            i = 0
            for ore in chunks(list(range(0, 20 - now.hour)), 3):
                for ora in ore:
                    ora = ora + now.hour
                    keyboard.add(i, InlineButton("{}".format(str(Time(hour=ora))),
                                                 "/{} {} {}".format(self.command(), edificio, ora)))
                i += 1
            keyboard.add(i, InlineButton("Adesso", "/{} {} {}".format(self.command(), edificio, now)))

            return self.replace("Per che ora vuoi controllare se ci sono aule libere?", keyboard)
        else:
            edificio = self.params()[0]
            when = Time.from_string(self.params()[1])
            self.replace("Consulto la timeline...")
            if not get_timeline(edificio):
                return self.replace("Errore caricamento timeline. Riprova!")

            text = "Aule libere per le {}\n".format(when)
            for aula in edifici[edificio]['aule']:
                free = True
                stato = ""
                if not len(aula['lezioni']):
                    stato = "libera"
                for lezione in aula['lezioni']:
                    if when >= lezione.start:
                        if not lezione.corso:
                            stato = "aula studio"
                        elif when >= lezione.end:
                            stato = "libera"
                        else:
                            stato = "occupata almeno fino alle {}".format(lezione.end)
                            free = False
                            break
                    elif lezione.corso:  # prossima lezione
                        stato = "libera fino alle {}".format(lezione.start)
                        break
                    else:
                        stato = "aula studio"
                if free:
                    text += "\u2705 {} {}\n".format(aula['nome'], stato)  # aula libera per ora
                else:
                    text += "\u274c {} {}\n".format(aula['nome'], stato)

            return self.replace(text)

    def timeline(self) -> Message:
        if not len(self.params()):
            keyboard = InlineKeyboard()
            keyboard.add(1, InlineButton("Monte generoso", "/{} mtg".format(self.command())))
            keyboard.add(2, InlineButton("Morselli", "/{} mrs".format(self.command())))
            keyboard.add(3, InlineButton("Seppilli", "/{} sep".format(self.command())))

            return self.answer("Scegli l'edificio:", keyboard)
        else:
            edificio = self.params()[0]
            self.replace("Consulto la timeline...")
            if not get_timeline(edificio):
                return self.replace("Errore caricamento timeline. Riprova!")
            if len(self.params()) == 1:
                keyboard = InlineKeyboard()
                aule = edifici[edificio]['aule']
                i = 0
                for aule in chunks(aule, 3):  # massimo 3 aule per riga
                    for aula in aule:
                        keyboard.add(i, InlineButton("{}".format(aula['nome']),
                                                     "/{} {} {}".format(self.command(), edificio, aula['nome'])))
                    i += 1
                keyboard.add(i, InlineButton("Tutte le aule",
                                             "/{} {} tutte".format(self.command(), edificio)))

                return self.replace("Scegli l'aula", keyboard)
            else:
                aula_edificio = " ".join(self.params()[1:])
                text = ""
                for aula in edifici[edificio]['aule']:
                    if aula['nome'] == aula_edificio or aula_edificio == "tutte":
                        text += "\n<b>{}</b>\n".format(aula['nome'])
                        if len(aula['lezioni']) > 0:
                            text += "\n".join(
                                "{}-{} {}".format(lezione.start, lezione.end, lezione.corso) for lezione
                                in aula['lezioni'])
                            text += "\n"
                if not text:
                    text = "Non sono presenti lezioni in {}!".format(aula_edificio)

                return self.replace(text)
