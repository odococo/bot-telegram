import json
import time

from commands.command import execute
from telegram.bot import Bot
from telegram.wrappers import Command


def polling(bot: Bot, last_update: int = 0, wait: int = 1):
    while True:
        updates = bot.get_updates(last_update)
        for update in updates:
            print(update)
            if update.message.reply_to and update.message.reply_to.original_from_user:
                bot.forward_message(update.message.reply_to.original_from_user.user_id, update.message.chat,
                                    update.message)
            elif isinstance(update.message, Command):
                execute(bot, update)
            else:
                bot.dump(update)
        last_update = updates[-1].update_id + 1 if len(updates) > 0 else last_update
        time.sleep(wait)


def discard(bot: Bot):
    updates = bot.get_updates()
    polling(bot, updates[-1].update_id + 1 if len(updates) > 0 else 0)


def main():
    bot = Bot("262354959:AAGZbji0qOxQV-MwzzRqiWJYdPVzkqrbC4Y")
    polling(bot)


if __name__ == "__main__":
    main()
