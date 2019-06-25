import logging

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
from telegram.wrappers import Update


def execute(bot: Bot, update: Update):
    commands = [
        Command(bot, update),
        Standard(bot, update),
        F1(bot, update),
        Insubria(bot, update),
        Loot(bot, update),
        Cron(bot, update),
        Lampo(bot, update),
        Sara(bot, update)
    ]
    command = update.message.command
    default = commands[0]
    c = command

    try:
        for command_type in commands:
            if hasattr(command_type, command):
                c = getattr(command_type, command)
                break
            elif command_type == Sara and update.message.from_user.user_id == sara:
                c = getattr(command_type, "tesoro")
                break
        else:
            c = getattr(default, "error")
        c()
    except Exception as e:
        logging.exception(e)
        getattr(default, "wrong")(c)
