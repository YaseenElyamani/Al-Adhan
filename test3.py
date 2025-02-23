from playsound import playsound
import time
from datetime import datetime
from apscheduler.schedulers.background import BlockingScheduler
from prayer import get_prayer_times, print_athan


def play_sound():
    playsound("audio/The Adhan - Omar Hisham.mp3")
    return

def adhan():
    times = get_prayer_times("toronto", "ca")
    #Testing
    #times = ["16:43", "16:47", "16:51", "16:55", "16:59"]
    scheduler = BlockingScheduler()
    print("Adhan Begun!")
    print_athan(times)
    for prayer_time in times:
        hour, minute = prayer_time.split(':')

        scheduler.add_job(play_sound, 'cron', hour=hour, minute=minute, id=f"adhan_{hour}_{minute}")

    print("Current Scheduled Jobs:")


    print(times)

    for job in scheduler.get_jobs():
        print(job)

    try:
        print("Press Ctrl+C to exit")
        scheduler.start()
        time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown(wait=False)
        print("Sheduler Stopped")

adhan()