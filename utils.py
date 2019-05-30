import datetime
import time
from dataclasses import dataclass

from bs4 import BeautifulSoup
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.remote.webdriver import WebDriver


@dataclass
class Date:
    """Classe di supporto per l'utilizzo di datetime"""
    date: datetime.datetime

    @classmethod
    def from_millis(cls, millis: int) -> 'Date':
        return cls(datetime.datetime.fromtimestamp(millis))

    @classmethod
    def now(cls) -> 'Date':
        return cls(datetime.datetime.now())

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

    def to_string(self, format_date: str) -> str:
        return self.date.strftime(format_date)

    def to_date(self) -> str:
        return self.to_string("%Y-%m-%d")

    def to_time(self) -> str:
        return self.to_string("%H:%M:%S")


@dataclass
class Time:
    ore: int
    minuti: int
    secondi: int

    @classmethod
    def from_string(cls, string: str):
        params = string.split(":")
        ore = int(params[0])
        minuti = int(params[1])
        if len(params) > 2:
            secondi = int(params[2])
        else:
            secondi = 0

        return cls(ore, minuti, secondi)


@dataclass
class WebScraper:
    driver: WebDriver

    @classmethod
    def chrome(cls):
        options = ChromeOptions()
        options.headless = True
        display = Display(visible=0, size=(800, 600))
        display.start()
        driver = webdriver.Chrome(options=options)

        return cls(driver)

    @classmethod
    def firefox(cls):
        options = FirefoxOptions()
        options.headless = True
        display = Display(visible=0, size=(800, 600))
        display.start()
        driver = webdriver.Firefox(options=options)

        return cls(driver)

    def get_page(self, url: str, wait: int = 1) -> BeautifulSoup:
        self.driver.get(url)
        time.sleep(wait)  # attesa per caricare la pagina

        return BeautifulSoup(self.driver.page_source, "html.parser")

    def quit(self):
        self.driver.quit()
