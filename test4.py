#NEED TO UNDERSTAND WHAT THIS CODE DOES, CAUSE I FORGOT, UNNECESSARY

            """
            if not self.current_prayer and int(current_hour) < int(hour):
                    self.current_prayer_time = prayer_time
                    self.current_prayer = prayer
            elif not self.current_prayer and int(current_hour) == int(hour) and int(current_minute) < int(minute):
                self.current_prayer_time = prayer_time
                self.current_prayer = prayer
            if not self.current_prayer and i == 5:
                self.current_prayer = PRAYERS[0]
                self.current_prayer_time = times[0]
            """


def update(self):

        if not self.scheduler.get_jobs():
            self.tomorrow_prayers()

        self.jobs = self.scheduler.get_jobs()
        current_job = self.jobs[0]

        next_job = min(self.jobs, key=lambda job: job.next_run_time)
        run_time = next_job.next_run_time
        job_id = next_job.id.capitalize()

        self.next_prayer = job_id
        
        now = datetime.datetime.now(run_time.tzinfo)
        diff = (run_time - now).total_seconds()

        for job in self.scheduler.get_jobs():
            if job.next_run_time and job.next_run_time <= now:
                self.scheduler.remove_job(job.id)
        
        if diff <= 0:
            self.next_prayer_label.configure(text=self.jobs[0].id)
        mins, secs = divmod(int(diff), 60)
        hrs, mins = divmod(mins, 60)
            
            

        diff_formatted = f"{hrs:02}:{mins:02}:{secs:02}"
        self.time_to_prayer.configure(text=diff_formatted)
        self.next_prayer_label.configure(text=current_job.id)

        self.after(1000, self.update)