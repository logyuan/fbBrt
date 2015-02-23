# coding: utf8
import subprocess
import time
import datetime
from datetime import timedelta

def HourlyUpdater():
    p = subprocess.Popen(['open', 'http://localhost:8088/fsr/graphAPI/HourlyUpdater'])
    time.sleep(1800)
    p.kill()
    return "Finished"

def DailyUpdater():
    p = subprocess.Popen(['open', 'http://localhost:8088/fsr/graphAPI/DailyUpdater'])
    time.sleep(1800)
    p.kill()
    return "Finished"

def NewsUpdater():
    p = subprocess.Popen(['open', 'http://localhost:8088/fsr/newsAPI/index'])
    time.sleep(1800)
    p.kill()
    return "Finished"

from gluon.scheduler import Scheduler
Now = datetime.datetime.now()
start_time = datetime.datetime.strftime(Now,'%Y-%m-%d 15:00:00')
start_time1 = datetime.datetime.strftime(Now,'%Y-%m-%d %H:%M:%S')
start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
start_time2 = datetime.datetime.strptime(start_time1, '%Y-%m-%d %H:%M:%S') + timedelta(minutes=5)
start_time3 = datetime.datetime.strptime(start_time1, '%Y-%m-%d %H:%M:%S') + timedelta(minutes=35)

scheduler = Scheduler(fbdb)

scheduler.queue_task('DailyUpdater', repeats = 0, period=3600*24, start_time=start_time)
scheduler.queue_task('HourlyUpdater', repeats = 0, period=3600, start_time=start_time2)
scheduler.queue_task('NewsUpdater', repeats = 0, period=3600, start_time=start_time3)
