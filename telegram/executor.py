import logging
from typing import List

from command.admin.lampo import Lampo
from command.admin.private.cron import Cron
from command.command import Command
from command.general.insubria import Insubria
from command.general.private.f1 import F1
from command.general.private.loot import Loot
from command.general.private.sara import Sara
from command.general.private.standard import Standard as StandardPrivate
from command.general.private.weather import Weather
from command.general.standard import Standard as StandardGeneral
from telegram.bot import Bot
from telegram.ids import logs, sara
from telegram.wrappers import Update


def get_commands_list(bot: Bot, update: Update) -> List[Command]:
    return [
        Command(bot, update),
        Cron(bot, update),
        Lampo(bot, update),
        F1(bot, update),
        Loot(bot, update),
        Sara(bot, update),
        StandardPrivate(bot, update),
        Weather(bot, update),
        Insubria(bot, update),
        StandardGeneral(bot, update)
    ]


def get_command(bot: Bot, update: Update, command: str) -> callable:
    commands = get_commands_list(bot, update)
    default = Command(bot, update)
    c = getattr(default, "error")
    for command_type in commands:
        if hasattr(command_type, command):
            if command_type.can_execute():
                c = getattr(command_type, command)
            break
        elif command_type == Sara and update.message.from_user.user_id == sara:
            c = getattr(command_type, "tesoro")
            break

    return c


def execute(bot: Bot, update: Update):
    command = update.message.command
    try:
        logging.debug(get_command(bot, update, command)())
    except Exception as e:
        logging.exception(e)
        bot.dump(to=logs, update=update, exception=str(e))
        getattr(Command(bot, update), "wrong")(command)
