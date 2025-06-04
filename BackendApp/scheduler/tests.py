from BackendApp.scheduler.core import Scheduler

import math
from datetime import datetime
import asyncio

async def print_sqrt():
    print("SQRT OF A IS: ", math.sqrt(45))

async def print_sqrt2(a):
    print("SQRT2 OF A IS: ", math.sqrt(a))

obj = Scheduler(5)
job = obj.create_job(
        print_sqrt,
        "at",
        None,
        time_str = "15:06",
        day="tuesday"
    )
job.tags = set("#1")

job = obj.create_job(
        print_sqrt2,
        "every",
        "minutes",
        1234,
        delay=5
    )
job.tags = set("#2")

job = obj.create_job(
        print_sqrt,
        "every_to",
        "hours",
        begin=5,
        end=10
    )
job.tags = set("#3")

async def scheduler_test():
    while True:
        await obj.pending()
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        print(f"{timestamp} - envoked; jobs: ", *obj.jobs)

if __name__ == "__main__":
    asyncio.run(scheduler_test())