from command.command import Command


class General(Command):
    def can_execute(self) -> bool:
        return super().can_execute()
