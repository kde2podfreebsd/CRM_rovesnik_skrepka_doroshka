import aioschedule
import asyncio 

class Scheduler(aioschedule.Scheduler):
    """
    Scheduler class inhereted from aioschdule.Scheduler with wrapper functions
    implementations for simplier use of aioschedule library 
    """
    def __init__(self, pending_delay: int):
        """
        __init__: creates a class instance of Scheduler

        :param pending_delay: when the time interval (in seconds), which is equal to pending delay, passes, envokes all the jobs in Scheduler.jobs
        """
        self.pending_delay = pending_delay
        super().__init__()
    
    def create_job(
            self, 
            job_func, 
            key: str, 
            time_unit: str,  
            *args, 
            **kwargs
        ) -> aioschedule.Job:
        """
        create_job: creates an insctance of a job in Scheduler.jobs and runs it accordingly to 
        the key and time_unit that have been passed

        Args:
            :param job_func: function for creating a job
            :param key: provides different ways of scheduling jobs
                - at: schedule a job at a specific time and day (or every day if nothig has been passed to :param day:)
                by passing :param time_str: in "XX:YY" format and :param day: as monday, tuesday, etc. respectively
                - every: schedule a job to be implemented every :param delay:
                - every_to: schedule a job to be implemented in time interval from :param begin: to :param end: 
                at a random moment of time 
            :param time_unit: initially is set to seconds
                - seconds 
                - minutes
                - hours
                - days
            :param kwargs: dictionary to pass params like time_str, delay, begin, end
            :param args: list to pass arguments for the job function

        Returns:
            aioschedule.Job
        
        To set Job.tags, retrieve Job object and set it manually
        """
        created_job = None
        if (key == "at"):
            if ("time_str" in kwargs):
                day = kwargs["day"] if "day" in kwargs else "day"
                created_job = eval(
                    f"""self.every().{day}.at(time_str=kwargs["time_str"]).do(
                        job_func,
                    ) if len(args) == 0 else self.every().day.at(time_str=kwargs["time_str"]).do(
                        job_func,
                        *args
                    )"""
                )
            else:
                raise(Exception("KeyError: Missing keyword time_str in kwargs"))

        elif (key == "every"):
            if ("delay" not in kwargs):
                raise(Exception("KeyError: Missing keyword delay in kwargs"))
            
            if (time_unit is None or time_unit == "seconds"):
                created_job = self.every(kwargs["delay"]).seconds.do(
                    job_func
                ) if len(args) == 0 else self.every(kwargs["delay"]).seconds.do(
                    job_func,
                    *args
                )
            elif (time_unit == "minutes"):
                created_job = self.every(kwargs["delay"]).minutes.do(
                    job_func
                ) if len(args) == 0 else self.every(kwargs["delay"]).minutes.do(
                    job_func,
                    *args
                )
            elif (time_unit == "hours"):
                created_job = self.every(kwargs["delay"]).hours.do(
                    job_func
                ) if len(args) == 0 else self.every(kwargs["delay"]).hours.do(
                    job_func,
                    *args
                )
            elif (time_unit == "days"):
                created_job = self.every(kwargs["delay"]).days.do(
                    job_func
                ) if len(args) == 0 else self.every(kwargs["delay"]).days.do(
                    job_func,
                    *args
                )
            else:
                raise(Exception("InvalidValue: time_unit can be only \"seconds\", \"minutes\", \"hours\" and \"days\""))
            
        elif (key == "every_to"):
            if (time_unit is None or time_unit == "seconds"):
                created_job = self.every(kwargs["begin"]).to(kwargs["end"]).seconds.do(
                    job_func=job_func
                ) if len(args) == 0 else self.every(kwargs["begin"]).to(kwargs["end"]).seconds.do(
                    job_func=job_func,
                    args=args
                )  
            elif (time_unit == "minutes"):
                created_job = self.every(kwargs["begin"]).to(kwargs["end"]).minutes.do(
                    job_func=job_func
                ) if len(args) == 0 else self.every(kwargs["begin"]).to(kwargs["end"]).minutes.do(
                    job_func=job_func,
                    args=args
                )
            elif (time_unit == "hours"):
                created_job = self.every(kwargs["begin"]).to(kwargs["end"]).hours.do(
                    job_func=job_func
                ) if len(args) == 0 else self.every(kwargs["begin"]).to(kwargs["end"]).hours.do(
                    job_func=job_func,
                    args=args
                )
            elif (time_unit == "days"):
                created_job = self.every(kwargs["begin"]).to(kwargs["end"]).days.do(
                    job_func=job_func
                ) if len(args) == 0 else self.every(kwargs["begin"]).to(kwargs["end"]).days.do(
                    job_func=job_func,
                    args=args
                )
            else:
                raise(Exception("InvalidValue: time_unit can be only \"seconds\", \"minutes\", \"hours\" and \"days\""))
        else:
            raise(Exception("InvalidValue: key can be only \"at\", \"every\" and \"every_to\""))
        
        return created_job


    def remove_job(self, tags: list):
        """
        remove_job: deletes all jobs in aioschedule.jobs if tags is None, otherwise deletes
        only jobs with specified tags in tags list 

        Args:
            :param tags: list of tags or None

        Rerturns:
            void 
        """
        if (tags is None):
            aioschedule.clear()
        else:
            for tag in tags:
                aioschedule.clear(tag=tag)
    
    async def run_job(self, job_func, *args):
        """
        run_job: run the job and immediately reschedule it

        Args:
            :param job_func: function for running
            :param args: functions' arguments
            
        Returns:
            the result of running job_func
        """
        self.job_func = job_func
        result = await self.run()
        self.job_func = None 
        return result 
    
    async def pending(self):
        await self.run_pending()
        await asyncio.sleep(self.pending_delay)