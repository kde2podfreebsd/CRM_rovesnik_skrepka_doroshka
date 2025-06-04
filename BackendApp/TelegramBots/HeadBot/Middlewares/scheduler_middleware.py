from datetime import datetime
from BackendApp.TelegramBots.HeadBot.Config import bot


class ScheduledTasks:

    _instance = None

    def __init__(self, scheduler):
        self.scheduler = scheduler
        self.existing_jobs = {}

    async def process(self):
        pass

    async def run(self):
        pass