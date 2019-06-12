import datetime as dt
import time
from dataclasses import dataclass
from typing import Union

from bs4 import BeautifulSoup
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.remote.webdriver import WebDriver


class DateTime(dt.datetime):

    def __new__(cls, year: int = 1900, month: int = 1, day: int = 1, hour: int = 0, minute: int = 0, second: int = 0,
                microsecond: int = 0, tzinfo=None, *, fold=0) -> 'DateTime':

        return super().__new__(cls, year, month, day, hour, minute, second, microsecond)

    @classmethod
    def from_datetime(cls, datetime: dt.datetime) -> Union['DateTime', 'Date', 'Time']:
        return cls(datetime.year, datetime.month, datetime.day, datetime.hour, datetime.minute, datetime.second)

    @classmethod
    def from_string(cls, datetime: str, dt_format: str = "%y-%m-%d %H:%M:%S") -> Union['DateTime', 'Date', 'Time']:
        return cls.from_datetime(dt.datetime.strptime(datetime, dt_format))

    @classmethod
    def from_millis(cls, millis: int) -> 'DateTime':
        return cls.from_datetime(dt.datetime.fromtimestamp(millis))

    @classmethod
    def by_now(cls):
        return super().__new__()

    def datetime(self) -> str:
        return super().__str__()

    def add(self, years: int = 0, months: int = 0, days: int = 0,
            hours: int = 0, minutes: int = 0, seconds: int = 0,
            milliseconds: int = 0) -> ['DateTime', 'Date', 'Time']:
        """
        year = 365 giorni
        month = 30 giorni
        hour = 3600 secondi
        minute = 60 secondi
        millisecond = 1000 microsecondi
        """
        d = 365 * years + 30 * months + days
        s = 3600 * hours + 60 * minutes + seconds
        m = 1000 * milliseconds
        return self.from_datetime(self + dt.timedelta(days=d, seconds=s, microseconds=m))

    def diff(self, other: 'DateTime', unit: str) -> float:
        """
        Differenza tra due date in un'unità di misura a scelta

        years = 365 giorni
        months = 30 giorni
        """
        delta = self - other
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


class Date(DateTime):
    def __str__(self):
        return str(self.date())

    def __eq__(self, other: 'Date') -> bool:
        return self.date() == other.date()

    def __gt__(self, other: 'Date') -> bool:
        return self.date() > other.date()

    def __ge__(self, other: 'Date') -> bool:
        return self.date() >= other.date()

    def __ne__(self, other: 'Date') -> bool:
        return self.date() != other.date()

    def __lt__(self, other: 'Date') -> bool:
        return self.date() < other.date()

    def __le__(self, other: 'Date') -> bool:
        return self.date() <= other.date()

    @classmethod
    def from_string(cls, d: str, date_format: str = None) -> 'Date':
        if date_format is not None:
            now = dt.datetime.now()
            d = "{} {}".format(d, now.strftime("%H:%M:%S"))
            return super().from_string(d, date_format)

        params = d.split("-")
        if len(params) == 1:
            return Date.from_string(d + "-01-01", "%y")
        elif len(params) == 2:
            return Date.from_string(d + "-01", "%y-%m")
        else:
            return Date.from_string(d, "%y-%m-%d")


class Time(DateTime):
    def __str__(self) -> str:
        return str(self.time())

    def __eq__(self, other: 'Time') -> bool:
        return self.time() == other.time()

    def __gt__(self, other: 'Time') -> bool:
        return self.time() > other.time()

    def __ge__(self, other: 'Time') -> bool:
        return self.time() >= other.time()

    def __ne__(self, other: 'Time') -> bool:
        return self.time() != other.time()

    def __lt__(self, other: 'Time') -> bool:
        return self.time() < other.time()

    def __le__(self, other: 'Time') -> bool:
        return self.time() <= other.time()

    @classmethod
    def from_string(cls, t: str, time_format: str = None) -> 'Time':
        if time_format is not None:
            now = dt.datetime.now()
            t = "{} {}".format(now.strftime("%y-%m-%d"), t)
            return super().from_string(t)

        params = t.split(":")
        if len(params) == 1:
            return Time.from_string(t + ":00:00", "%H")
        elif len(params) == 2:
            return Time.from_string(t + ":00", "%H:%M")
        else:
            return Time.from_string(t, "%H:%M:%S")


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

    @classmethod
    def phantomjs(cls):
        driver = webdriver.PhantomJS()

        return cls(driver)

    def get_page(self, url: str, wait: int = 1) -> BeautifulSoup:
        self.driver.get(url)
        time.sleep(wait)  # attesa per caricare la pagina

        return BeautifulSoup(self.driver.page_source, "html.parser")

    def quit(self):
        self.driver.quit()


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]
