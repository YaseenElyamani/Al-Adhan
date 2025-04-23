from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import time

def jake():
    print("Jake's job is running!")

def paul():
    print("Paul's job is running!")

def yaseen():
    print("Yaseen's job is running!")

# Initialize scheduler
scheduler = BackgroundScheduler()

# Schedule jobs at specific times (24-hour format)
scheduler.add_job(jake, CronTrigger(hour=5, minute=36), id='jake')
scheduler.add_job(paul, CronTrigger(hour=10, minute=0), id='paul')
scheduler.add_job(yaseen, CronTrigger(hour=17, minute=0), id='yaseen')

scheduler.start()

# Give time to initialize
time.sleep(1)

# Function to get the next job and countdown
def display_next_job_countdown():
    jobs = scheduler.get_jobs()
    if not jobs:
        print("No jobs scheduled.")
        return

    # Get the job with the soonest next run time
    next_job = min(jobs, key=lambda job: job.next_run_time)
    run_time = next_job.next_run_time
    job_id = next_job.id.capitalize()

    print(f"\nNext job to run: {job_id}")
    print(f"Scheduled for: {run_time.strftime('%I:%M %p')}")

    while True:
        now = datetime.now(run_time.tzinfo)
        diff = (run_time - now).total_seconds()

        if diff <= 0:
            print(f"\n{job_id}'s job is running now!")
            break

        mins, secs = divmod(int(diff), 60)
        hrs, mins = divmod(mins, 60)
        print(f"{job_id}: {hrs:02}:{mins:02}:{secs:02}", end='\r')
        time.sleep(1)

# Run the countdown
display_next_job_countdown()


"""

jobs = sorted(
    [job for job in self.scheduler.get_jobs() if job.next_run_time],
    key=lambda job: job.next_run_time
)

# Find current job index
current_index = next((i for i, job in enumerate(jobs) if job.id == self.current_prayer), -1)

# Get next job with wrap-around
if current_index != -1:
    next_index = (current_index + 1) % len(jobs)
    next_job = jobs[next_index]
    self.next_prayer = next_job.id
    self.next_prayer_label.configure(text=self.next_prayer)

"""