"""
reads schedule information from config and schedules jobs
"""
import schedule
from collections import deque
from conf import o_conf
from functools import partial
from utils.logger import logger


class ScheduleSetter:
    def __init__(self, job, schedule_settings):
        # parse schedule section
        self.repeat_patterns = schedule_settings.schedule
        for repeat_pattern in self.repeat_patterns:
            if repeat_pattern in ['every heartbeat', 'always']:
                schedule.every(o_conf().heartbeat_secs).seconds.do(job)
            else:
                tokens = deque(repeat_pattern.split())
                type_token = tokens.popleft()
                if type_token == 'daily':
                    tokens.popleft()
                    schedule.every().day.at(tokens.popleft()).do(job)
                if type_token == 'every':
                    interval, time_unit = tokens
                    schedule.every(int(interval)).set_unit(time_unit).do(job)

    def runner(self, listener):
        logger.info("Listening to {ind}:({clazz}){lst}...".format(ind=listener.indicator_name,
            clazz=listener.listener_class, lst=listener.name))
        listener.poll()

# NB!! (09/06/2016)
# Hotfix needed in scheduler library (class Jobs):
#    def set_unit(self, unit):
#         # unit should be plural
#         self.unit = unit if unit[-1] == 's' else unit + 's'
#         return self
