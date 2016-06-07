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
                components = deque(repeat_pattern.split())
                current = components.popleft()
                if current == 'at':
                    schedule.every().day.at(components.popleft()).do(monitor.poll)
                if current == 'every':
                    interval, time_unit = components
                    schedule.every(interval).unit(time_unit).do(monitor.poll)