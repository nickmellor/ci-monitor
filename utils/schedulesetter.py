"""
reads schedule information from config and schedules jobs
"""
import schedule
from collections import deque
from conf import o_conf


class ScheduleSetter:
    def __init__(self, monitor, settings):
        # parse schedule section
        self.repeat_patterns = settings.schedule
        for repeat_pattern in self.repeat_patterns:
            if repeat_pattern in ['every heartbeat', 'always']:
                schedule.every(o_conf().defaults.heartbeat_secs).seconds.do(monitor.poll)
            else:
                tokens = deque(repeat_pattern.split())
                type_token = tokens.popleft()
                if type_token == 'at':
                    schedule.every().day.at(tokens.popleft()).do(monitor.poll)
                if type_token == 'every':
                    interval, time_unit = tokens
                    schedule.every(int(interval)).set_unit(time_unit).do(monitor.poll)


# NB!! (09/06/2016)
# Hotfix needed in scheduler (Jobs class):
#    def set_unit(self, unit):
#         # unit should be plural
#         self.unit = unit if unit[-1] == 's' else unit + 's'
#         return self
