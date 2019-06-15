from dataclasses import dataclass
from typing import Dict, Set

from commands.commands import Command
from telegram.wrappers import User, Message
from utils import Time

jobs: Dict[User, Set[str]] = {}


@dataclass
class Cron(Command):

    def avvisa(self) -> Message:
        """
        Manda un messaggio a un utente/chat arbitraria

        Sintassi:
        /avvisa id_chat/utente da_quando ogni_quanto unità_di_misura messaggio

        id_chat/utente è l'id (numero) o l'username della chat
        da_quando è now oppure un'ora (formato hh::MM)
        ogni_quanto è un valore intero
        unità_di_misura un valore tra weeks/days/hours/minutes/seconds
        messaggio è il testo da mandare
        :return:
        """
        from_user = self.from_user()
        to_chat = int(self.params()[0])
        once = True
        if self.params()[1] == "now":
            from_when = Time.by_now().add(minutes=1)
        else:
            from_when = Time.from_string(self.params()[1])
        if self.params()[2].isnumeric():
            once = False
            every = int(self.params()[2])
            unit_time = self.params()[3]
            time_details = {'start_date': from_when, unit_time: every}
            what = " ".join(self.params()[4:])
        else:
            time_details = {'run_date': from_when}
            what = " ".join(self.params()[2:])

        job_id = self.bot.add_cron_job(lambda: self.bot.send_message(chat_id=to_chat, text=what), single=once,
                                       time_details=time_details)
        if not once:
            jobs.setdefault(from_user, set())
            jobs[from_user].add(job_id)

        return self.answer("Il cronjob è stato correttamente settato con id: <code>{}</code>".format(job_id))

    def getavvisi(self) -> Message:
        if self.from_user() in jobs and jobs[self.from_user()]:
            text = "Lista avvisi:\n"
            avvisi = "\n". join(["Avviso: <code>{}</code>".format(job) for job in jobs[self.from_user()]])

            return self.answer(text + avvisi)
        else:
            return self.answer("Non hai reminder attivi")

    def stopavviso(self) -> Message:
        job_id = self.params()[0]
        jobs.get(self.from_user(), set()).discard(job_id)
        self.bot.remove_cron_job(job_id)

        return self.answer("Rimosso reminder")

    def stopavvisi(self) -> Message:
        if self.from_user() in jobs:
            for job_id in jobs[self.from_user()]:
                self.bot.remove_cron_job(job_id)
            del jobs[self.from_user()]

            return self.answer("Cancellati tutti i reminder")
        else:
            return self.answer("Non hai reminder attivi")
