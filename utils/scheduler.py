"""
reads schedule information from config and provides services
"""
from collections import deque

import schedule

from conf import o_conf


class Scheduler:
    def __init__(self, job, settings):
        # parse schedule section
        self.repeat_patterns = settings.schedule
        for repeat_pattern in self.repeat_patterns:
            if repeat_pattern in ['every heartbeat', 'always']:
                schedule.every(o_conf().defaults.schedule.heartbeat).seconds.do(job)
            components = deque(repeat_pattern.split())
            current = components.popleft()
            if current == 'at':
                schedule.every().day.at(components.pop()).do(job)
            if current == 'every':
                interval, time_unit = components
                schedule.every(interval).unit(time_unit).do(job)


def job():
    print('Hello, world!')

if __name__ == '__main__':
    schedule.every(5).seconds.do(job)
    while(1):
        schedule.run_pending()
