import customtkinter as ctk
from prayer import get_prayer_times, print_athan, get_prayer_times_lat, get_tomorrow_prayer_times_lat, get_tomrrow_prayer_times
from apscheduler.schedulers.background import BackgroundScheduler
import pygame
from tkinter import PhotoImage
import pystray
from PIL import Image, ImageTk
from time import *
import datetime
from datetime import timedelta
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
import json
import urllib3

PRAYERS = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


#Grabs location of the user, returns: lat and long, city, and country
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


 
#App using ctkinter 
class App(ctk.CTk):
    def __init__(self):
        super().__init__()

    
        #Initialize Background Scheduler
        pygame.mixer.init()
        self.scheduler = BackgroundScheduler()
        self.load_settings()
        self.scheduler.start()
        self.prayers_setup()
        self.setup_menu()
        self.border()
        self.label_grid()
        self.scheduler_setup()
        self.setup_window()
        self.timer()
        
        
        
        
        
        
        #self.debug_trigger_prayers()
        #self.debug_tomorrow_prayers()

        # --- tray icon setup ---
        #self.tray_icon = None
        self.create_tray_icon()
        self.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)  # intercept close button

    
        
    def timer(self):

        #Initialize and display next prayer label in the countdown timer to the next prayer
        
        self.jobs = self.scheduler.get_jobs()

        if self.jobs:
            first_job_id = self.jobs[0].id
        else:
            first_job_id = "Next prayer"

        if not self.jobs:
            self.tomorrow_prayers()
            self.jobs = self.scheduler.get_jobs()

        self.next_prayer_label = ctk.CTkLabel(self.circle_frame, text=first_job_id, font=("Itim", 28), bg_color="transparent")
        self.next_prayer_label.grid(row=0, column=0,padx=0,pady=0, sticky="nsew")

        #Countdown timer to the next prayer
        self.time_to_prayer = ctk.CTkLabel(self.circle_frame, text="بِسْمِ ٱللهِ   ", font=("Amiri", 36), bg_color="transparent")
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

        
        self.after(1000, self.update)
    def load_settings(self):
            try:
                with open("settings.json", "r") as f:
                    data = json.load(f)
                    self.city = data.get("city", "")
                    self.country = data.get("country", "")
            except FileNotFoundError:
                self.city = ""
                self.country = ""

    def create_tray_icon(self):
        """Create tray icon once and keep it hidden initially"""
        image = Image.open("images/logo.ico").resize((64, 64))
        self.tray_icon = pystray.Icon(
            "PrayerTimes",
            image,
            "Prayer Times",
            menu=pystray.Menu(
                pystray.MenuItem("Show", self.restore_from_tray),
                pystray.MenuItem("Quit", self.quit_app)
            )
        )

        # Start the icon in the main thread but keep hidden
        import threading
        threading.Thread(target=self.tray_icon.run, daemon=True).start()
        self.tray_icon.visible = False

    def minimize_to_tray(self):
        """Hide window, show tray icon"""
        self.withdraw()
        if self.tray_icon:
            self.tray_icon.visible = True  # just show it, don’t rerun

    def restore_from_tray(self, icon=None, item=None):
        """Restore window from tray"""
        self.deiconify()
        if self.tray_icon:
            self.tray_icon.visible = False


    def quit_app(self, icon=None, item=None):
        """Quit the app completely"""
        if self.tray_icon:
            self.tray_icon.stop()
        self.destroy()

    def setup_menu(self):
        # Use standard Tkinter Menu
        from tkinter import Menu

        menubar = Menu(self)
        self.config(menu=menubar)

        # File menu
        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label="Settings", command=self.open_settings)
        file_menu.add_command(label="Quit", command=self.quit_app)
        menubar.add_cascade(label="File", menu=file_menu)



    def open_settings(self):
        settings_window = ctk.CTkToplevel(self)
        settings_window.title("Settings")
        settings_window.geometry("400x300")

        # Force it to the front
        settings_window.transient(self)     # tie it to main window
        settings_window.grab_set()           # modal (blocks main window)
        settings_window.lift()               # raise above all
        settings_window.focus_force()         # keyboard focus



        #Grid Label
        location_label = ctk.CTkLabel(settings_window, text="Location Settings")
        location_label.pack()

        
        #Grid Frame
        location_frame = ctk.CTkFrame(settings_window)
        location_frame.pack(expand=True, padx=0,pady=0)

        location_frame.grid_columnconfigure(0, weight=0)

        country_label = ctk.CTkLabel(location_frame, text="Enter Country:")
        country_label.grid(row=0, column=-0, padx=5, pady=5, sticky="n")
        
        country_input = ctk.CTkEntry(location_frame, placeholder_text="Enter Country")
        country_input.grid(row=0, column=1, padx=5, pady=5, sticky="n")

        city_label = ctk.CTkLabel(location_frame, text="Enter City:")
        city_label.grid(row=1, column=-0, padx=5, pady=5, sticky="n")
        
        city_input = ctk.CTkEntry(location_frame, placeholder_text="Enter City")
        city_input.grid(row=1, column=1, padx=5, pady=5, sticky="n")

        if self.city:
            city_input.configure(placeholder_text = self.city)
        if self.country:
            country_input.configure(placeholder_text = self.country)

        
        
        def save_settings():
            data = {
                "city": city_input.get(),
                "country": country_input.get()
            }
            with open("settings.json", "w") as f:
                json.dump(data, f)
            
            self.country = data["country"]
            self.city = data["city"]

            self.prayers_setup()
            self.restart_prayers() #restart prayer times
            settings_window.destroy()

        save_btn = ctk.CTkButton(settings_window, text="Save", command=save_settings)
        save_btn.pack(pady=20)
        
        



    #Initializes title of app, resizability, icon and size
    def setup_window(self):
        self.resizable(True, True)
        self.title("Prayer Times")
        self.iconbitmap('images/logo.ico')
        self.geometry("900x550")

    

    def border(self): 
        #Main Grid holding prayer times grid and layout/borders grid
        self.main_grid = ctk.CTkFrame(self,width=860, height = 500, bg_color="transparent", fg_color="transparent")
        self.main_grid.place(relx=0.5, rely=0.5, anchor="center")

        #rectangular border
        border = Image.open("images/border.png")
        border = border.resize((860, 500)) # Border Resizing
        self.border = ImageTk.PhotoImage(border)
        
        
        self.border_label = ctk.CTkLabel(self.main_grid, image=self.border, text="")
        #self.border_label.place(relx=0.5, rely=0.5, anchor="center")  # Position the image
        self.border_label.grid(row=0, column=0, sticky="nsew")


        self.circular_grid = ctk.CTkFrame(self,width=0, height = 0, bg_color="transparent", fg_color="transparent")
        self.circular_grid.place(relx=0.79, rely=0.5, anchor="center")
        #circular border 1
        circular_border = Image.open("images/circle_border.png")
        self.circular_border = ImageTk.PhotoImage(circular_border)
        

        self.circular_border_label = ctk.CTkLabel(self.circular_grid, image=self.circular_border, text="")
        #self.circular_border_label.place(relx=0.79, rely=0.5, anchor="center")
        self.circular_border_label.grid(row=0, column=0, padx=0, sticky="")

        #circular border 2
        circular_border2 = circular_border.resize((195, 195))
        self.circular_border2 = ImageTk.PhotoImage(circular_border2)

        self.circular_border2_label = ctk.CTkLabel(self.circular_grid, image=self.circular_border2, text="")
        #self.circular_border2_label.place(relx=0.79, rely=0.5, anchor="center")
        self.circular_border2_label.grid(row=0, column=0, padx=0, sticky="")


    def label_grid(self):

        #Grid frame to hold prayer times labels
        self.grid_frame = ctk.CTkFrame(self, width=200, height=100, corner_radius=10)
        self.grid_frame.place(relx=0.05, rely=0.21)

        self.circle_frame = ctk.CTkFrame(self, width=100, height=100, corner_radius=10, bg_color="transparent", fg_color="transparent")
        self.circle_frame.place(relx=0.715, rely=0.43)


        #prayer times labels put into grid frame

        self.title_label = ctk.CTkLabel(self.grid_frame, text="Prayer Times", font=("Itim", 36))
        self.title_label.grid(row=0, column=0,padx=80,pady=10, sticky="w", columnspan=2)
        #self.suhoor_label = ctk.CTkLabel(self.grid_frame, text="Suhoor Time: ", font=("IstokWeb",24))
        #self.suhoor_label.grid(row=1, column=0,padx=20,pady=10, sticky="w")
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
        
    def prayers_setup(self):

        #Grab location of the user using the function get_location
        lat, lon, city, country = get_location()

        if self.city and self.country:
            self.times = get_prayer_times(self.city, self.country)
        else:
            self.times = get_prayer_times_lat(lat, lon)

        now = datetime.datetime.now()

        

        isha_time_str = self.times[PRAYERS.index("Isha")]
        isha_hour, isha_minute = map(int, isha_time_str.split(":"))
        isha_datetime = now.replace(hour=isha_hour, minute=isha_minute, second=0, microsecond=0)


        if now > isha_datetime:
        # Past Isha, so load tomorrow's prayers instead
            if self.city and self.country:
                self.times = get_tomrrow_prayer_times(self.city, self.country)
            else:
                self.times = get_tomorrow_prayer_times_lat(lat, lon)

        

    def scheduler_setup(self):


        #Iterate through prayer times and add as job, as well as display prayer times

        self.prayer_times_list = []  # Create a list to store labels
        i = 1
        for prayer_time, prayer in zip(self.times, PRAYERS):
            
            #In each iteration, split hours and minutes for each prayer time
            hour, minute = prayer_time.split(':')

            #set display_hour to 12hr time 
            display_hour = f"{int(hour)}"
            if int(hour) < 12:
                meridiem = 'AM'
                
            else:
                if int(hour) > 12:
                    display_hour = f"{int(hour) - 12}"
                meridiem = 'PM'


            #Add prayer time labels on grid frame 
            self.prayer_time_label = ctk.CTkLabel(self.grid_frame, text=f"{display_hour}:{minute} {meridiem}", font=("IstokWeb",24))
            self.prayer_time_label.grid(row=i, column=1, sticky="e", padx=30)
            self.prayer_times_list.append(self.prayer_time_label)


            run_datetime = datetime.datetime.now().replace(hour=int(hour), minute=int(minute), second=0, microsecond=0)
            
            # ADD JOB TO SCHEDULER
            self.scheduler.add_job(self.play_sound_and_show_button, 'date', run_date=run_datetime, id=prayer)  
            #self.scheduler.add_job(self.play_sound_and_show_button, 'cron', hour=19, minute=9, second=20)
    
            
            i += 1
    
    def restart_prayers(self):
        self.scheduler.remove_all_jobs()

        for label in self.prayer_times_list:
            label.destroy()
        self.prayer_times_list.clear()

        self.scheduler_setup()

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



        """
        self.job = self.scheduler.get_job(self.current_prayer)
        jobs = self.scheduler.get_jobs()
        self.next_prayer = min(jobs, key=lambda job: self.job.next_run_time)


        
        now = datetime.datetime.now(self.job.next_run_time.tzinfo)
        time_diff = self.job.next_run_time - now

        total_seconds = int(time_diff.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        diff_formatted = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            

        self.time_to_prayer.configure(text=diff_formatted)

        self.after(1000, self.update)
        """

    def tomorrow_prayers(self):
        lat, lon, city, country = get_location()
        if self.city and self.country:
            self.times = get_tomrrow_prayer_times(self.city, self.country)
        else:
            self.times = get_tomorrow_prayer_times_lat(lat, lon)

        i = 0
        for time, prayer in zip(self.times, PRAYERS):
            hour, minute = time.split(":")

            #set display_hour to 12hr time 
            display_hour = f"{int(hour)}"
            if int(hour) < 12:
                meridiem = 'AM'
                
            else:
                if int(hour) > 12:
                    display_hour = f"{int(hour) - 12}"
                meridiem = 'PM'

            self.prayer_times_list[i].configure(text = f"{display_hour}:{minute} {meridiem}")

            run_datetime = (datetime.datetime.now() + timedelta(days=1)).replace(hour=int(hour), minute=int(minute), second=0, microsecond=0)
            self.scheduler.add_job(self.play_sound_and_show_button, 'date', run_date=run_datetime, id=prayer)


    def play_sound_and_show_button(self):
        # Restore the window if it's minimized
        if not self.winfo_viewable():  # checks if window is hidden
            self.deiconify()
            self.lift()  # bring window to front
            self.focus_force()  # give it focus

        self.play_sound()
        self.show_button()
        self.after(180000, self.hide_button)
   
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

    def debug_trigger_prayers(self, delay=20):
        """Schedule all prayers to trigger in a few seconds for testing"""
        self.scheduler.remove_all_jobs()

        now = datetime.datetime.now()
        for i, prayer in enumerate(PRAYERS):
            run_time = now + timedelta(seconds=delay + i * 3)
            self.scheduler.add_job(
                self.play_sound_and_show_button,
                'date',
                run_date=run_time,
                id=prayer
            )

        print("DEBUG: Scheduled prayers starting in", delay, "seconds")

    def debug_tomorrow_prayers(self, delay=5):
        """Schedule tomorrow prayers to trigger in a few seconds for testing"""
        self.scheduler.remove_all_jobs()  # Clear current jobs
        lat, lon, city, country = get_location()
        tmrw_times = get_tomorrow_prayer_times_lat(lat, lon)

        now = datetime.datetime.now()
        for i, (time, prayer) in enumerate(zip(tmrw_times, PRAYERS)):
            # Schedule each prayer a few seconds apart
            run_time = now + timedelta(seconds=delay + i * 3)
            self.scheduler.add_job(
                self.play_sound_and_show_button,
                'date',
                run_date=run_time,
                id=f"Tomorrow-{prayer}"
            )

        print(f"DEBUG: Tomorrow prayers scheduled starting in {delay} seconds")




if __name__ == "__main__":
    app = App()
    app.mainloop()
