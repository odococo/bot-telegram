from dataclasses import dataclass
from typing import Dict, List

import bs4

from commands.commands import Command
from telegram.wrappers import InlineKeyboard, InlineButton
from utils import WebScraper, Date, Time

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
    le = {
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
        le['lezioni'].append(lezione)

    return le


@dataclass
class InsubriaCommands(Command):
    driver = None

    def aule(self) -> Dict:
        if not len(self.params()):
            keyboard = InlineKeyboard()
            keyboard.add(1, InlineButton("Monte generoso", "/{} mtg".format(self.command())))
            keyboard.add(2, InlineButton("Morselli", "/{} mrs".format(self.command())))
            keyboard.add(3, InlineButton("Seppilli", "/{} sep".format(self.command())))

            return self.answer("Scegli l'edificio:", keyboard)
        else:
            global edifici
            global tries

            url = "http://timeline.uninsubria.it/browse.php?sede={}"
            edificio = self.params()[0]
            if edificio not in edifici or edifici[edificio]['data'].date.day != Date.now().date.day:
                print("web scraping per {}".format(edificio))
                self.replace("Consulto la timeline...")

                scraper = WebScraper.firefox()
                timeline = scraper.get_page(url.format(edificio), tries)
                self.replace("Elaboro i dati...")

                lezioni = []
                aule = timeline.find_all('tr')
                for i in range(1, len(aule)):
                    lezioni.append(_get_aula(aule[i]))

                if len(lezioni) > 0:
                    edifici[edificio] = {
                        'data': Date.now(),
                        'lezioni': lezioni  # lista di aule
                    }
                    tries = 1
                else:
                    tries += 1

                    return self.replace("Errore caricamento timeline. Riprova!")
                scraper.quit()

            text = ""
            for lezioni in edifici[edificio]['lezioni']:
                now = Time.now()
                free = True
                stato = ""
                if not len(lezioni['lezioni']):
                    stato = "libera fino a fine giornata"
                for j, lezione in enumerate(lezioni['lezioni']):
                    if now >= lezione.start:
                        if not lezione.corso:
                            stato = "aula studio"
                        elif now >= lezione.end:
                            stato = "libera fino a fine giornata"
                        else:
                            stato = "occupata fino alle {}".format(lezione.end)
                            free = False
                            break
                    elif lezione.corso:  # prossima lezione
                        stato = "libera fino alle {}".format(lezione.start)
                    else:
                        stato = "aula studio"
                if free:
                    text += "\u2705 {} {}\n".format(lezioni['nome'], stato)  # aula libera per ora
                else:
                    text += "\u274c {} occupata\n".format(lezioni['nome'])

            return self.replace(text)
