from dataclasses import dataclass
from typing import Dict, List

import bs4

from commands.commands import Command
from telegram.wrappers import InlineKeyboard, InlineButton
from utils import WebScraper, Date, Time


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


@dataclass
class InsubriaCommands(Command):
    edifici: Dict = None
    driver = None

    def _get_aula(self, aula: bs4.element.Tag) -> Dict[str, List[_Lezione]]:
        lezioni = [lezione.find('div') for lezione in
                   aula.find_all('td', {'class': "filled"})]  # trovo tutte le aule in cui c'e' una lezione
        nome_aula = lezioni[0].text
        le = {
            'nome': nome_aula,
            'lezioni': []
        }
        for i in range(1, len(lezioni)):
            params = lezioni[i].find_all('div')
            print(params)
            ora = params[1].text.split(" - ")
            facolta = params[2].text
            dettagli = params[3].text
            corso = params[4].text if len(params) > 4 else ""
            lezione = _Lezione(Time.from_string(ora[0]), Time.from_string(ora[1]), facolta, dettagli, corso)
            le['lezioni'].append(lezione)

        return le

    def aule(self) -> Dict:
        if not len(self.params()):
            keyboard = InlineKeyboard()
            keyboard.add(1, InlineButton("Monte generoso", "/{} mtg".format(self.command())))
            keyboard.add(2, InlineButton("Morselli", "/{} mrs".format(self.command())))
            keyboard.add(3, InlineButton("Seppilli", "/{} sep".format(self.command())))

            return self.answer("Scegli l'edificio:", keyboard)
        else:
            if self.edifici is None:
                self.edifici = {}
            url = "http://timeline.uninsubria.it/browse.php?sede={}"
            edificio = self.params()[0]
            if edificio not in self.edifici:
                scraper = WebScraper.chrome()
                timeline = scraper.get_page(url.format(edificio))
                self.edifici[edificio] = timeline

            aule = self.edifici[edificio].find_all('tr')

            text = ""
            for i in range(1, len(aule)):
                lezioni = self._get_aula(aule[i])
                text += "Aula {}".format(lezioni['nome'])
                now = Date.now()
                if not len(lezioni['lezioni']):
                    text += " e' libera tutto il giorno\n"
                    continue
                for j, lezione in enumerate(lezioni['lezioni']):
                    if now.date.hour > lezione.start.ore and now.date.hour > lezione.end.ore:
                        if j + 1 > len(lezioni['lezioni']):
                            text += " libera dalle {} fino a fine giornata\n".format(lezione.end.ore)
                            break
                        elif now.date.hour < lezioni['lezioni'][j + 1].start.ore:
                            text += " libera da adesso fino alle {}\n".format(lezioni['lezioni'][i + 1].start.ore)
                            break
                    elif now.date.hour < lezione.start.ore:
                        text += " libera da adesso fino alle {}\n".format(lezione.start.ore)
                        break
                else:
                    text += " non e' libera attualmente\n"
            return self.replace(text)
