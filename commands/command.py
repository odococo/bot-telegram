from commands.commands import Command
from commands.lampo_commands import LampoCommands
from commands.loot_commands import LootCommands
from commands.sara_commands import SaraCommands
from commands.standard_commands import Standard
from telegram.bot import Bot
from telegram.ids import lampo, sara
from telegram.wrappers import Update


def execute(bot: Bot, update: Update):
    command = update.message.command
    default = Command(bot, update)
    standard = Standard(bot, update)
    loot = LootCommands(bot, update)
    lc = LampoCommands(bot, update)
    sc = SaraCommands(bot, update)
    c = command

    try:
        if hasattr(standard, command):
            c = getattr(standard, command)
            c()
        elif hasattr(loot, command):
            c = getattr(loot, command)
            c()
        elif update.message.from_user.user_id == sara:
            if hasattr(sc, command):
                c = getattr(sc, command)
                c()
            else:
                c = getattr(sc, "tesoro")
                c(command)
        elif update.message.from_user.user_id == lampo:
            if hasattr(lc, command):
                c = getattr(lc, command)
                c()
            else:
                c = getattr(default, "error")
                c(command)
        else:
            c = getattr(default, "error")
            c(command)
    except Exception as e:
        print(e)
        getattr(default, "wrong")(c)