from dataclasses import dataclass
from typing import List, Dict

from commands.standard_commands import Standard
from telegram.wrappers import InlineKeyboard, InlineButton, Message
from utils import join, DateTime, get_json

bandiere = {

}

cache = {

}

url_classifica = {
    'piloti': "driverStandings",
    'costruttori': "constructorStandings"
}


@dataclass
class _Pilota:
    tag: str
    name: str
    posizione_partenza: int
    posizione_arrivo: int
    giro_veloce: str

    def __str__(self):
        return "{}: {} -> {}".format(self.tag, self.posizione_partenza, self.posizione_arrivo)


@dataclass
class _Gara:
    stagione: int
    round: int
    data: DateTime
    nome: str
    citta: str
    nazione: str
    piloti: List[_Pilota] = None


@dataclass
class F1(Standard):
    url = "https://ergast.com/api/f1/current{}.json"

    def _scelta_gara(self, attuale: bool = False, new: bool = True) -> Message:
        keyboard = InlineKeyboard(3)
        for gara in self._get_gare():
            keyboard.add(InlineButton(
                "{}[{}]".format(gara.citta, gara.nazione),
                "/{} {} {}".format(self.command(), join(self.params(), " "), gara.round)))
        if attuale:
            keyboard.add_next_line(
                InlineButton("Attuale", "/{} {} attuale".format(self.command(), join(self.params(), " "))))

        if new:
            return self.answer("Scegli la gara", keyboard)
        else:
            return self.replace("Scegli la gara", keyboard)

    def _get_url(self, *params):
        prefix = "/" if params else ""
        params = params or ("",)
        return self.url.format(join([str(param) for param in params], prefix=prefix, separator="/"))

    def _get_gare(self) -> List[_Gara]:
        gare = get_json(self._get_url())['MRData']['RaceTable']['Races']

        return [_Gara(gara['season'], gara['round'],
                      DateTime.from_string("{} {}".format(gara['date'], gara['time']), "%Y-%m-%d %H:%M:%SZ"),
                      gara['Circuit']['circuitName'], gara['Circuit']['Location']['locality'],
                      gara['Circuit']['Location']['country']) for gara in gare]

    def _get_gara(self, num_gara: int) -> _Gara:
        url = self._get_url(num_gara)
        dettagli = get_json(url)['MRData']['RaceTable']['Races'][0]
        gara = _Gara(dettagli['season'], dettagli['round'],
                     DateTime.from_string("{} {}".format(dettagli['date'], dettagli['time']), "%Y-%m-%d %H:%M:%SZ"),
                     dettagli['Circuit']['circuitName'], dettagli['Circuit']['Location']['locality'],
                     dettagli['Circuit']['Location']['country'])
        if gara.data < DateTime.by_now():
            url = self._get_url(num_gara, "results")
            dettagli = get_json(url)['MRData']['RaceTable']['Races'][0]
            gara.piloti = [_Pilota(pilota['Driver']['code'], pilota['Driver']['driverId'], int(pilota['grid']),
                                   pilota['position'], pilota['FastestLap']['Time']['time']) for pilota in
                           dettagli['Results']]

        return gara

    def _get_classifica(self, tipologia_classifica: str, gara: str) -> Dict:
        gara = "" if gara == "attuale" else int(gara)
        url = self._get_url(gara, url_classifica[tipologia_classifica])
        classifica = get_json(url)['MRData']['StandingsTable']['StandingsLists']
        if tipologia_classifica == "piloti":
            return self._get_classifica_piloti(classifica)
        else:
            return self._get_classifica_costruttori(classifica)

    @staticmethod
    def _get_classifica_piloti(classifica: List) -> Dict:
        if not classifica:
            return {}
        classifica = classifica[0]['DriverStandings']

        return {pilota['Driver']['driverId']: pilota['points'] for pilota in classifica}

    @staticmethod
    def _get_classifica_costruttori(classifica: List) -> Dict:
        if not classifica:
            return {}
        classifica = classifica[0]['ConstructorStandings']

        return {costruttore['Constructor']['constructorId']: costruttore['points'] for costruttore in classifica}

    def risultati(self) -> Message:
        if not self.params():
            return self._scelta_gara()
        else:
            gara = self._get_gara(int(self.params()[0]))

            if gara.piloti:
                return self.replace(join(gara.piloti, "\n"))
            else:
                return self.replace("La gara non si e' ancora svolta. Programmazione per {}".format(gara.data))

    def classifica(self) -> Message:
        if not self.params():
            keyboard = InlineKeyboard()
            keyboard.add(
                InlineButton("Classifica piloti", "/{} piloti".format(self.command())),
                InlineButton("Classifica costruttori", "/{} costruttori".format(self.command()))
            )

            return self.answer("Scegli la classifica da visualizzare:", keyboard)
        elif len(self.params()) == 1:
            return self._scelta_gara(attuale=True)
        else:
            scelta_classifica = self.params()[0]
            scelta_gara = self.params()[1]
            classifica = self._get_classifica(scelta_classifica, scelta_gara)
            if not classifica:
                return self.replace("La gara scelta non è ancora stata disputata!")

            return self.replace(join(["{}: {}".format(nome, punti) for nome, punti in classifica.items()], "\n"))

    def apif1(self) -> Message:
        return self.answer("Le informazioni per la Formula1 sono prese da <a href='https://ergast.com/mrd/'>qua</a>")
