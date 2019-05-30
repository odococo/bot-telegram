from dataclasses import dataclass
from typing import Dict, List

import bs4

from commands.commands import Command
from telegram.wrappers import InlineKeyboard, InlineButton
from utils import WebScraper, Date, Time

edifici: Dict = {}


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


def get_aula(aula: bs4.element.Tag) -> Dict[str, List[_Lezione]]:
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
            url = "http://timeline.uninsubria.it/browse.php?sede={}"
            edificio = self.params()[0]
            if edificio not in edifici or edifici[edificio]['data'].date.day != Date.now().date.day:
                self.replace("Consulto la timeline...")
                scraper = WebScraper.firefox()
                timeline = scraper.get_page(url.format(edificio))

                lezioni = []
                aule = timeline.find_all('tr')
                for i in range(1, len(aule)):
                    lezioni.append(get_aula(aule[i]))
                edifici[edificio] = {
                    'data': Date.now(),
                    'lezioni': lezioni  # lista di aule
                }
                scraper.quit()

            text = ""
            for lezioni in edifici[edificio]['lezioni']:
                now = Date.now()
                stato = ""
                if not len(lezioni['lezioni']):
                    stato = "libera tutto il giorno"
                for j, lezione in enumerate(lezioni['lezioni']):
                    if now.date.hour > lezione.start.ore and now.date.hour > lezione.end.ore:
                        if j + 1 > len(lezioni['lezioni']):
                            stato = "libera dalle {} fino a fine giornata".format(lezione.end.ore)
                            break
                        elif now.date.hour < lezioni['lezioni'][j + 1].start.ore:
                            stato = "libera da adesso fino alle {}".format(lezioni['lezioni'][j + 1].start.ore)
                            break
                        else:
                            break
                    elif now.date.hour < lezione.start.ore:
                        stato = "libera da adesso fino alle {}".format(lezione.start.ore)
                        break
                    else:
                        break
                if stato:
                    text += "\u2705 {} {}\n".format(lezioni['nome'], stato)  # aula libera per ora
                else:
                    text += "\u274c {} occupata\n".format(lezioni['nome'])
            return self.replace(text)
