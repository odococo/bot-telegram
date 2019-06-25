import logging
import random
import time
from typing import List

import requests

from commands.command import execute
from commands.insubria_commands import get_timeline
from telegram.bot import Bot
from telegram.ids import lampo, sara
from telegram.wrappers import Command
from utils import Time

logging.basicConfig(level=logging.INFO)


def polling(bot: Bot, last_update: int = 0, wait: int = 1):
    while True:
        updates = bot.get_updates(last_update)
        for update in updates:
            if update.message.reply_to and update.message.reply_to.original_from_user:
                bot.forward_message(update.message.reply_to.original_from_user.user_id, update.message.chat,
                                    update.message)
            elif isinstance(update.message, Command):
                execute(bot, update)
            elif update.message.chat.chat_id == lampo:
                bot.dump(update=update.update)
        last_update = updates[-1].update_id + 1 if len(updates) > 0 else last_update
        time.sleep(wait)


def discard(bot: Bot):
    updates = bot.get_updates()
    polling(bot, updates[-1].update_id + 1 if len(updates) > 0 else 0)


def cron_jobs(bot: Bot):
    bot.add_cron_job(lambda: _get_timelines(['mtg', 'mrs', 'sep']), single=False,
                     time_details={'start_date': Time.by_now_with(hour=0, minute=5), 'days': 1})
    bot.add_cron_job(lambda: bot.dump(ip=requests.get("http://ipinfo.io?").json()), single=False,
                     time_details={'hours': 4})
    _send_reminders(bot)


def _get_timelines(edifici: List[str]):
    for edificio in edifici:
        while not get_timeline(edificio):
            logging.info("Ritento a consulare la timeline di {}".format(edificio))


def _send_reminders(bot: Bot):
    #  TODO se si mette un'ora fissa, l'invio verrà eseguito più volte
    #  tante quante riesce in quel minuto o secondo
    #  probabilmente specificando anche i microsecondi si riesce a eseguirlo una volta
    hour = random.randint(19, 23)
    minute = random.randint(0, 59)
    bot.add_cron_job(lambda: _send_reminder(bot, hour, minute), single=True,
                     time_details={'run_date': Time.by_now_with(hour=hour, minute=minute)})


def _send_reminder(bot: Bot, hour: int, minute: int):
    bot.send_message(sara, "Forgot something? Sono le {}:{}".format(hour, minute))
    _send_reminders(bot)


def main():
    try:
        bot = Bot("262354959:AAGZbji0qOxQV-MwzzRqiWJYdPVzkqrbC4Y")
        cron_jobs(bot)
        polling(bot)
    except requests.exceptions.ConnectionError:
        time.sleep(1)
        main()


if __name__ == "__main__":
    main()
