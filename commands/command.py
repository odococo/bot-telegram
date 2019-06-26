import logging
from typing import List, Callable

from commands.commands import Command
from commands.cron_commands import Cron
from commands.f1_commands import F1
from commands.insubria_commands import Insubria
from commands.lampo_commands import Lampo
from commands.loot_commands import Loot
from commands.sara_commands import Sara
from commands.standard_commands import Standard
from telegram.bot import Bot
from telegram.ids import sara
from telegram.wrappers import Update, Message


def get_commands_list(bot: Bot, update: Update) -> List[Command]:
    return [
        Command(bot, update),
        Standard(bot, update),
        F1(bot, update),
        Insubria(bot, update),
        Loot(bot, update),
        Cron(bot, update),
        Lampo(bot, update),
        Sara(bot, update)
    ]


def get_command_instance(cls: str, bot: Bot, update: Update):
    return globals()[cls](bot, update)


def get_command(bot: Bot, update: Update, command: str):
    commands = get_commands_list(bot, update)
    default = Command(bot, update)
    for command_type in commands:
        if hasattr(command_type, command):
            if command_type.can_execute():
                c = getattr(command_type, command)
            else:
                c = getattr(default, "unauthorized")
            break
        elif command_type == Sara and update.message.from_user.user_id == sara:
            c = getattr(command_type, "tesoro")
            break
    else:
        c = getattr(default, "error")

    return c


def execute(bot: Bot, update: Update):
    command = update.message.command
    try:
        get_command(bot, update, command)()
    except Exception as e:
        logging.exception(e)
        getattr(Command(bot, update), "wrong")(command)
