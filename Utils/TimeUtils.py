import datetime
from dataclasses import dataclass


@dataclass
class Date:
    """Classe di supporto per l'utilizzo di datetime"""
    date: datetime.datetime

    @classmethod
    def from_millis(cls, millis: int) -> 'Date':
        return cls(datetime.datetime.fromtimestamp(millis / 1000.0))

    def __str__(self) -> str:
        return str(self.date)

    def add(self, years: int = 0, months: int = 0, days: int = 0,
            hours: int = 0, minutes: int = 0, seconds: int = 0,
            milliseconds: int = 0, microseconds: int = 0) -> 'Date':
        """
        year = 365 giorni
        month = 30 giorni
        hour = 3600 secondi
        minute = 60 secondi
        millisecond = 1000 microsecondi
        """
        d = 365 * years + 30 * months + days
        s = 3600 * hours + 60 * minutes + seconds
        m = 1000 * milliseconds + microseconds
        return Date(self.date + datetime.timedelta(days=d, seconds=s, microseconds=m))

    def strict_add(self, years: int = 0, months: int = 0, days: int = 0,
                   hours: int = 0, minutes: int = 0, seconds: int = 0,
                   microseconds: int = 0):
        """Aggiunge semplicemente l'unita' di misura
        Solleva una ValueError se si oltrepassa il range dei campi"""
        return Date(datetime.datetime(self.date.year + years, self.date.month + months,
                                      self.date.day + days, self.date.hour + hours,
                                      self.date.minute + minutes, self.date.second + seconds,
                                      self.date.microsecond + microseconds))

    def diff(self, other: 'Date', unit: str) -> float:
        """
        years = 365 giorni
        months = 30 giorni
        """
        delta = self.date - other.date
        switcher = {
            'years': delta.days / 30 / 365,
            'months': delta.days / 30,
            'days': delta.days,
            'hours': delta.days * 24,
            'minutes': delta.days * 24 * 60,
            'seconds': delta.days * 24 * 60 + delta.seconds,
            'milliseconds': (delta.days * 24 * 60 + delta.seconds) * 1000,
            'microseconds': (delta.days * 24 * 60 + delta.seconds) * 1000 * 1000
        }
        return switcher.get(unit, "Unita' non valida")

    def to_string(self, format: str) -> str:
        return self.date.strftime(format)

    def to_date(self) -> str:
        return self.to_string("%Y-%m-%d")

    def to_time(self) -> str:
        return self.to_string("%H:%M:%S")
