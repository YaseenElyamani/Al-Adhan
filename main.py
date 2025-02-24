import customtkinter as ctk
from prayer import get_prayer_times, print_athan, get_prayer_times_lat
from apscheduler.schedulers.background import BackgroundScheduler
import pygame
from tkinter import PhotoImage
from PIL import Image, ImageTk
from time import *
import datetime
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
import json
import urllib3

PRAYERS = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

def get_location():
    url = 'http://ip-api.com/json'
    http = urllib3.PoolManager()
    response = http.request("GET", url)
    data = json.loads(response.data.decode('utf-8'))  # Decode the response and load JSON

    city = data['city']
    country = data['countryCode']

    lat = data['lat']
    lon = data['lon']

    return lat, lon, city.lower(), country.lower()


 # Hard code location// for testing

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        lat, lon, city, country = get_location()
        times = get_prayer_times_lat(lat, lon)

        self.resizable(True, True)
        self.title("Prayer Times")
        self.iconbitmap('images/logo.ico')
        self.geometry("900x550")

        #rectangular border
        border = Image.open("images/border.png")
        border = border.resize((860, 500)) # Border Resizing
        self.border = ImageTk.PhotoImage(border)
        
        
        self.border_label = ctk.CTkLabel(self, image=self.border, text="")
        self.border_label.place(relx=0.5, rely=0.5, anchor="center")  # Position the image

        #circular border 1
        circular_border = Image.open("images/circle_border.png")
        self.circular_border = ImageTk.PhotoImage(circular_border)
        

        self.circular_border_label = ctk.CTkLabel(self, image=self.circular_border, text="")
        self.circular_border_label.place(relx=0.79, rely=0.5, anchor="center")

        #circular border 2
        circular_border2 = circular_border.resize((195, 195))
        self.circular_border2 = ImageTk.PhotoImage(circular_border2)

        self.circular_border2_label = ctk.CTkLabel(self, image=self.circular_border2, text="")
        self.circular_border2_label.place(relx=0.79, rely=0.5, anchor="center")

        self.grid_frame = ctk.CTkFrame(self, width=200, height=100, corner_radius=10)
        self.grid_frame.place(relx=0.05, rely=0.21)

        self.circle_frame = ctk.CTkFrame(self, width=100, height=100, corner_radius=10, bg_color="transparent", fg_color="transparent")
        self.circle_frame.place(relx=0.715, rely=0.43)

        self.title_label = ctk.CTkLabel(self.grid_frame, text="Prayer Times", font=("Itim", 36))
        self.title_label.grid(row=0, column=0,padx=80,pady=10, sticky="w", columnspan=2)
        self.fajr_label = ctk.CTkLabel(self.grid_frame, text="Fajr Time: ", font=("IstokWeb",24))
        self.fajr_label.grid(row=1, column=0,padx=20,pady=10, sticky="w")
        self.dhuhr_label = ctk.CTkLabel(self.grid_frame, text="Dhuhr Time: ", font=("IstokWeb",24))
        self.dhuhr_label.grid(row=2, column=0,padx=20,pady=10, sticky="w")
        self.asr_label = ctk.CTkLabel(self.grid_frame, text="Asr Time: ", font=("IstokWeb",24))
        self.asr_label.grid(row=3, column=0,padx=20,pady=10, sticky="w")
        self.maghrib_label = ctk.CTkLabel(self.grid_frame, text="Maghrib Time: ", font=("IstokWeb",24))
        self.maghrib_label.grid(row=4, column=0,padx=20,pady=10, sticky="w")
        self.isha_label = ctk.CTkLabel(self.grid_frame, text="Isha Time: ", font=("IstokWeb",24))
        self.isha_label.grid(row=5, column=0,padx=20,pady=10, sticky="w")


        #Display current time - May not need this, just for testing
        self.current_time = strftime("%I:%M:%S %p")
        current_hour = int(datetime.datetime.now().strftime("%H"))
        current_minute = int(datetime.datetime.now().strftime("%M"))
        self.current_prayer = None
        self.next_prayer = None
        
        
        #self.current_time_label.place(relx=0.72, rely=0.58) font size 24

        

        #Initialize Background Scheduler
        self.scheduler = BackgroundScheduler()
        #Initialize Pygame for Audio
        pygame.mixer.init()
        #Iterate through prayer times and add as job, as well as display prayer times
        i = 1
        for prayer_time, prayer in zip(times, PRAYERS):

            hour, minute = prayer_time.split(':')

            display_hour = f"{int(hour)}"
            if int(hour) < 12:
                meridiem = 'AM'
                
            else:
                if int(hour) > 12:
                    display_hour = f"{int(hour) - 12}"
                meridiem = 'PM'

            self.prayer_time_label = ctk.CTkLabel(self.grid_frame, text=f"{display_hour}:{minute} {meridiem}", font=("IstokWeb",24))
            self.prayer_time_label.grid(row=i, column=1, sticky="e", padx=30)



            # ADD JOB TO SHEDULER
            self.scheduler.add_job(self.play_sound_and_show_button, 'cron', hour=hour, minute=minute, id=prayer)  
            #self.scheduler.add_job(self.play_sound_and_show_button, 'cron', hour=19, minute=9, second=20)


            if not self.current_prayer and int(current_hour) < int(hour):
                    self.current_prayer_time = prayer_time
                    self.current_prayer = prayer
            elif not self.current_prayer and int(current_hour) == int(hour) and int(current_minute) < int(minute):
                self.current_prayer_time = prayer_time
                self.current_prayer = prayer
            if not self.current_prayer and i == 5:
                self.current_prayer = PRAYERS[0]
                self.current_prayer_time = times[0]
            i += 1


        #Start Background Scheuduler
        self.scheduler.start()


        self.next_prayer_label = ctk.CTkLabel(self.circle_frame, text=self.current_prayer, font=("Itim", 28), bg_color="transparent")
        self.next_prayer_label.grid(row=0, column=0,padx=0,pady=0, sticky="nsew")

        self.time_to_prayer = ctk.CTkLabel(self.circle_frame, text=self.current_time, font=("Itim", 36), bg_color="transparent")
        self.time_to_prayer.grid(row=1, column=0,padx=0,pady=0, sticky="nsew")


        #Tick Scheduler
        self.after(1000, self.check_scheduler)
        
        #Stop button 
        stop_button_image = PhotoImage(file="images/stop_button.png")
        stop_button_image = stop_button_image.subsample(3, 3)

        self.overlay_button = ctk.CTkButton(self,image=stop_button_image, 
                                            text="", 
                                            fg_color="transparent", bg_color="transparent", 
                                            hover_color="#333333", 
                                            width = 250, height=220, corner_radius=0,
                                            command=self.stop)
        #self.show_button() #For testing

        
        self.update()

    def update(self):

        if self.next_prayer:
            self.current_prayer = self.next_prayer
        self.job = self.scheduler.get_job(self.current_prayer)
        if self.job and self.job.next_run_time:
            now = datetime.datetime.now(self.job.next_run_time.tzinfo)
            time_diff = self.job.next_run_time - now

            total_seconds = int(time_diff.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            diff_formatted = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            

        self.time_to_prayer.configure(text=diff_formatted)

        self.after(1000, self.update)

    def play_sound_and_show_button(self):
        self.play_sound()
        self.show_button()

        jobs = self.scheduler.get_jobs()
        next_job = min(jobs, key=lambda job: self.job.next_run_time or datetime.datetime.max)
        self.next_prayer = next_job.id

        self.next_prayer_label.configure(text=self.next_prayer)

    def hide_button(self):
        self.overlay_button.place_forget()
    def show_button(self):
        self.overlay_button.place(relx=0.79, rely=0.5, anchor="center")
    def play_sound(self):
        pygame.mixer.music.load("audio/The Adhan - Omar Hisham.mp3")
        pygame.mixer.music.play(loops=0)
    def stop(self):
        pygame.mixer.music.stop()
        self.hide_button()

    def check_scheduler(self):
        # Keeps the scheduler running in the background and updates the GUI
        if self.scheduler.get_jobs():
            self.after(1000, self.check_scheduler)


if __name__ == "__main__":
    app = App()
    app.mainloop()
