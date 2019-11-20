from dataclasses import dataclass

from command.general.private.private import Private
from utils import get_json, DateTime


@dataclass
class Weather(Private):
    def _make_map_api_call(self, op: str, z, x, y, date: int = DateTime.by_now().timestamp(), opacity: float = 0.8,
                           palette=None, fill_bound: bool = False, arrow_step: int = 32, use_norm: bool = False):
        """
        https://openweathermap.org/api/weather-map-2

        :param op: weather map layer
        :param z: number of zoom level
        :param x: number of x tile coordinate
        :param y: number of y tile coordinate
        :param date: date and time
        :param opacity: Degree of layer opacity. Available value from 0 to 1
        :param palette: color palette. {value}:{HEX color};..;{value}:{HEX color}
        :param fill_bound: all weather values outside the specified set of values will be filled by color corresponding
                to the nearest specified value
        :param arrow_step: step of values for drawing wind arrows, specify in pixels
        :param use_norm: the length of the arrows is normalizing
        :return:
        """
        url = 'http://maps.openweathermap.org/maps/2.0/weather/'
        key = 'b77171814f0f585d55579122914ff9f7'
        params = {
            'op': op,
            'z': z,
            'x': x,
            'y': y,
            'appid': key,
            'date': date,
            'opacity': opacity,
            'palette': palette,
            'fill_bound': fill_bound,
            'arrow_step': arrow_step,
            'use_norm': use_norm
        }

        return get_json(url, params=params)

    def _make_api_call(self):
        pass

    def current(self):
        city = self.params(as_string=True)
        params = {
            'q': city
        }
