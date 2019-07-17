import logging
import random
import sys
import time
from typing import List

import requests

from commands.command import execute
from commands.insubria_commands import get_timeline
from telegram.bot import Bot, params
from telegram.ids import lampo, sara
from telegram.wrappers import Command
from utils import Time, get_json

logging.basicConfig(level=logging.INFO)

last_ip = -1


def polling(bot: Bot, last_update: int = 0, wait: int = 1):
    while True:
        updates = bot.get_updates(last_update)
        for update in updates:
            logging.debug(update)
            if update.message.reply_to and update.message.reply_to.original_from_user:
                bot.forward_message(update.message.reply_to.original_from_user.user_id, update.message.chat,
                                    update.message)
            elif isinstance(update.message, Command):
                execute(bot, update)
            elif update.message.chat.chat_id == lampo:
                bot.debug(update=update)
        last_update = updates[-1].update_id + 1 if len(updates) > 0 else last_update
        time.sleep(wait)


def discard(bot: Bot):
    updates = bot.get_updates()
    avvisati = set()
    for update in updates:
        if update.message.from_user:
            chat_id = update.message.from_user.user_id
            if chat_id not in avvisati:
                avvisati.add(chat_id)
                bot.send_message(chat_id=chat_id, text="Bot online. Rimanda il comando!")
    polling(bot, updates[-1].update_id + 1 if len(updates) > 0 else 0)


def cron_jobs(bot: Bot):
    _get_ip(bot)
    # bot.add_cron_job(lambda: _get_timelines(['mtg', 'mrs', 'sep']), single=False,
    #                 time_details={'start_date': Time.by_now_with(hour=0, minute=5), 'days': 1})
    bot.add_cron_job(lambda: _get_ip(bot), single=False, time_details={'hours': 4})
    bot.add_cron_job(lambda: _send_memo(bot), single=False,
                     time_details={'start_date': Time.by_now_with(hour=18, minute=25), 'days': 1})
    _send_reminders(bot)


def _get_ip(bot: Bot):
    global last_ip

    ip = get_json("http://ipinfo.io?")['ip']
    if ip != last_ip:
        last_ip = ip
        bot.send_message(lampo, "L'ip è cambiato: {}".format(ip))


def _get_timelines(edifici: List[str]):
    for edificio in edifici:
        while not get_timeline(edificio):
            logging.info("Ritento a consultare la timeline di {}".format(edificio))


def _send_memo(bot: Bot):
    bot.send_message(sara, "Sono le 18.25")
    params['presa'] = False


def _send_reminders(bot: Bot):
    #  TODO se si mette un'ora fissa, l'invio verrà eseguito più volte
    #  tante quante riesce in quel minuto o secondo
    #  probabilmente specificando anche i microsecondi si riesce a eseguirlo una volta
    hour = random.randint(21, 23)
    minute = random.randint(0, 59)
    hour = 21
    minute = 58
    bot.add_cron_job(lambda: _send_reminder(bot, hour, minute), single=True,
                     time_details={'run_date': Time.by_now_with(hour=hour, minute=minute)})
    bot.add_cron_job(lambda: _check_presa(bot), single=True,
                     time_details={'run_date': Time.by_now_with(hour=hour, minute=(minute + 10) % 60)})


def _send_reminder(bot: Bot, hour: int, minute: int):
    if not params['presa']:
        bot.send_message(sara, "Forgot something? Sono le {}:{}".format(hour, minute))
    _send_reminders(bot)


def _check_presa(bot: Bot):
    if not params['presa']:
        bot.send_message(lampo, "Ricordale di prenderla!")


def main():
    bot = Bot(sys.argv[0])
    cron_jobs(bot)
    while True:
        try:
            discard(bot)
            polling(bot)
        except requests.exceptions.ConnectionError:
            time.sleep(10)


if __name__ == "__main__":
    main()
