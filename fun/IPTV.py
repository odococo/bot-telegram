import json
import re
from typing import Tuple

import requests


class IPTV:
    def __init__(self,
                 url: str = None):
        self.home = '/home/odococo/iptv/'
        self.original = self.home + 'original.m3u'
        if url:
            self.url = url
            self._save()

    def _save(self):
        response = requests.get(self.url)
        with open(self.original, 'w') as original:
            original.write(response.text)

    @staticmethod
    def _len(file: str):
        i = 0
        with open(file) as f:
            for line in f:
                if Link(line).ok:
                    f.readline()
                    i += 1
        return i

    def list_categories(self):
        channels = {}
        with open(self.original, 'r') as original:
            for line in original:
                link = Link(line)
                if link.ok:
                    channels.setdefault(link.category, []).append(link.name)
        print(json.dumps(channels, indent=2, sort_keys=True))

    def filter(self, file: str = '', categories: Tuple = ()):
        if file and categories:
            file = self.home + file
            with open(self.original, 'r') as original, open(file, 'w') as filtered:
                for line in original:
                    if Link(line).check(categories):
                        filtered.write(line + original.readline())
        else:
            file = self.original
        print('Canali aggiornati per {}: {}'.format(file[19:-4], self._len(file)))


class Link:
    def __init__(self, link: str):
        self.ok = link.startswith('#EXTINF')
        if self.ok:
            params = re.compile('\\w+-\\w+=').split(link)[-1].split(',')
            self.category, self.name = params[0][1:-1], params[1]

    def check(self, categories: Tuple[str] = ()):
        return self.ok and self.category and self.category in categories


def all_channels():
    IPTV('http://halloffame.liveyourlifeandcarpediem.biz:25461/'
         'get.php?username=zlampo&password=12345&type=m3u_plus&output=ts').filter()


def filter_all():
    altro = 'BASSA DEFINIZIONE/SD', 'NOTIZIE', 'TVSAT', 'TVSAT+1'
    paytv = ('CULTURA', 'INTRATTENIMENTO', 'Ondemand England', 'PREMIUM CINEMA', 'SKY CINEMA',
             'SKY PRIMAFILA LIVE', 'SKY PRIMAFILA ONDEMAND')
    sport = 'DAZN', 'SKY CALCIO', 'SKY SPORT', 'SPORT'
    saghe = ('FILM MARVEL', 'Saga Agente 007', 'Saga Il Pianeta Delle Scimmie', 'Saghe Film',
             'Saghe Horror')
    film = ('FILM AGGIORNATI IN HD', 'FILM NETFLIX', 'Film 4K', 'Film Animazione', 'Film Avventura',
            'Film Azione', 'Film Commedia', 'Film Crimine', 'Film Drammatici', 'Film Famiglia',
            'Film Fantascienza', 'Film Guerra', 'Film Horror', 'Film Mafia', 'Film Thriller',
            'I Mitici Di Walt Disney', 'ULTIMI INSERITI')
    serie = ('Serie Tv 1-1000', 'Serie Tv A-B', 'Serie Tv C-D', 'Serie Tv E-F', 'Serie Tv G-H',
             'Serie Tv I-J', 'Serie Tv K-L', 'Serie Tv M-N', 'Serie Tv O-P', 'Serie Tv Q-R',
             'Serie Tv S-T', 'Serie Tv U-V', 'Serie Tv W-X', 'ULTIME SERIE TV INSERITE')
    IPTV().filter('filtered.m3u', altro + paytv + sport + saghe + film + serie)


def standard():
    altro = 'BASSA DEFINIZIONE/SD', 'NOTIZIE', 'TVSAT', 'TVSAT+1'
    paytv = ('CULTURA', 'INTRATTENIMENTO', 'Ondemand England', 'PREMIUM CINEMA', 'SKY CINEMA',
             'SKY PRIMAFILA LIVE', 'SKY PRIMAFILA ONDEMAND')
    sport = 'DAZN', 'SKY CALCIO', 'SKY SPORT', 'SPORT'
    IPTV().filter('standard.m3u', altro + paytv + sport)


def list_categories():
    IPTV().list_categories()


if __name__ == '__main__':
    all_channels()
    filter_all()
    standard()
