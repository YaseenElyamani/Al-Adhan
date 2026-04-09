import customtkinter as ctk
from prayer import (
    PRAYERS,
    get_prayer_times,
    get_prayer_times_lat,
    get_tomorrow_prayer_times,
    get_tomorrow_prayer_times_lat,
)
from apscheduler.schedulers.background import BackgroundScheduler
import pygame
from tkinter import PhotoImage
import pystray
from PIL import Image, ImageTk
from time import strftime
import datetime
from datetime import timedelta
import json
import logging
import urllib3
import sys
import ctypes
import os
import winreg
import threading

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


# ---------------------------------------------------------------------------
# Path / startup helpers
# ---------------------------------------------------------------------------

def get_base_path():
    """Folder containing the running script or the frozen exe."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def resource_path(*parts):
    """Build a path relative to the app's base directory."""
    return os.path.join(get_base_path(), *parts)


def get_settings_path():
    return resource_path("settings.json")


def get_log_path():
    return resource_path("prayer_times.log")


# Configure file-based logging. We avoid print() because PyInstaller's
# --noconsole mode leaves stdout as None on some Windows configs, which
# would crash any print call.
logging.basicConfig(
    filename=get_log_path(),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("prayer_times")


def add_to_startup():
    """Register the app to launch on Windows login."""
    if getattr(sys, "frozen", False):
        # Packaged exe: launch the exe directly.
        value = f'"{sys.executable}"'
    else:
        # Dev mode: launch the script with the current Python.
        script_path = os.path.abspath(__file__)
        value = f'"{sys.executable}" "{script_path}"'

    reg_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    name = "PrayerTimesApp"

    try:
        registry_key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(registry_key, name, 0, winreg.REG_SZ, value)
        winreg.CloseKey(registry_key)
        log.info("Added to startup successfully!")
    except Exception as e:
        log.warning("Failed to add to startup: %s", e)


# Keep the mutex handle alive for the lifetime of the process so it isn't
# garbage-collected (which would release the mutex and defeat the check).
_INSTANCE_MUTEX = None


def single_instance():
    global _INSTANCE_MUTEX
    _INSTANCE_MUTEX = ctypes.windll.kernel32.CreateMutexW(
        None, False, "Global\\PrayerTimesAppMutex"
    )
    if ctypes.windll.kernel32.GetLastError() == 183:
        sys.exit(0)


single_instance()


# ---------------------------------------------------------------------------
# Misc helpers
# ---------------------------------------------------------------------------

def get_location():
    """
    Returns (lat, lon, city, country) using ip-api.com.
    Returns (None, None, None, None) on any failure so callers can fall
    back to user-provided settings instead of crashing the app.
    """
    try:
        http = urllib3.PoolManager()
        response = http.request("GET", "http://ip-api.com/json", timeout=10.0)
        data = json.loads(response.data.decode("utf-8"))
        return (
            data["lat"],
            data["lon"],
            data["city"].lower(),
            data["countryCode"].lower(),
        )
    except Exception as e:
        log.warning("get_location failed: %s", e)
        return None, None, None, None


def format_12hr(hour, minute):
    """Accepts ints (preferred) or numeric strings for hour/minute."""
    hour = int(hour)
    minute = int(minute)
    meridiem = "AM" if hour < 12 else "PM"
    display_hour = hour % 12 or 12
    return f"{display_hour}:{minute:02d} {meridiem}"


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.check_startup()

        self.resizable(False, False)
        self.title("Prayer Times")
        try:
            self.iconbitmap(resource_path("images", "logo.ico"))
        except Exception as e:
            log.warning("Could not set window icon: %s", e)
        self.geometry("900x550")

        try:
            pygame.mixer.init()
            self.audio_ready = True
        except Exception as e:
            log.warning("pygame.mixer.init failed; adhan playback disabled: %s", e)
            self.audio_ready = False

        self.scheduler = BackgroundScheduler()
        self.last_checked = datetime.datetime.now()
        self.times = None

        self.load_settings()
        self.scheduler.start()
        self.prayers_setup()
        self.setup_menu()
        self.draw_borders()
        self.label_grid()
        self.scheduler_setup()
        self.timer()

        self.tray_icon = None
        self.create_tray_icon()
        self.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)

    # ------------------------------------------------------------------
    # Startup / settings
    # ------------------------------------------------------------------

    def check_startup(self):
        settings_path = get_settings_path()
        try:
            with open(settings_path, "r") as f:
                data = json.load(f)
        except Exception:
            data = {}

        if not data.get("startup_added"):
            add_to_startup()
            data["startup_added"] = True
            try:
                with open(settings_path, "w") as f:
                    json.dump(data, f)
            except Exception as e:
                log.warning("Could not write settings.json: %s", e)

    def load_settings(self):
        settings_path = get_settings_path()
        try:
            with open(settings_path, "r") as f:
                data = json.load(f)
            self.city = data.get("city", "")
            self.country = data.get("country", "")
        except (FileNotFoundError, json.JSONDecodeError):
            self.city = ""
            self.country = ""

    # ------------------------------------------------------------------
    # Tray
    # ------------------------------------------------------------------

    def create_tray_icon(self):
        try:
            image = Image.open(resource_path("images", "logo.ico")).resize((64, 64))
        except Exception as e:
            log.warning("Could not load tray icon: %s", e)
            return

        self.tray_icon = pystray.Icon(
            "PrayerTimes",
            image,
            "Prayer Times",
            menu=pystray.Menu(
                pystray.MenuItem("Show", self.restore_from_tray),
                pystray.MenuItem("Quit", self.quit_app),
            ),
        )
        threading.Thread(target=self.tray_icon.run, daemon=True).start()
        self.tray_icon.visible = False

    def minimize_to_tray(self):
        self.withdraw()
        if self.tray_icon:
            self.tray_icon.visible = True

    def restore_from_tray(self, icon=None, item=None):
        self.deiconify()
        if self.tray_icon:
            self.tray_icon.visible = False

    def quit_app(self, icon=None, item=None):
        if self.tray_icon:
            self.tray_icon.stop()
        self.destroy()

    # ------------------------------------------------------------------
    # Menu / settings window
    # ------------------------------------------------------------------

    def setup_menu(self):
        from tkinter import Menu

        menubar = Menu(self)
        self.config(menu=menubar)

        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label="Settings", command=self.open_settings)
        file_menu.add_command(label="Quit", command=self.quit_app)
        menubar.add_cascade(label="File", menu=file_menu)

    def open_settings(self):
        settings_window = ctk.CTkToplevel(self)
        settings_window.title("Settings")
        settings_window.geometry("400x300")
        try:
            settings_window.iconbitmap(resource_path("images", "settings.ico"))
        except Exception:
            pass
        settings_window.resizable(False, False)
        settings_window.transient(self)
        settings_window.grab_set()
        settings_window.lift()
        settings_window.focus_force()

        location_label = ctk.CTkLabel(
            settings_window, text="Location Settings", font=("Itim", 24, "bold")
        )
        location_label.pack(pady=(80, 0))

        location_frame = ctk.CTkFrame(settings_window)
        location_frame.pack(expand=True, padx=0, pady=0)
        location_frame.grid_columnconfigure(0, weight=0)

        country_label = ctk.CTkLabel(location_frame, text="Enter Country:")
        country_label.grid(row=0, column=0, padx=5, pady=5, sticky="n")
        country_input = ctk.CTkEntry(location_frame, placeholder_text="Enter Country")
        country_input.grid(row=0, column=1, padx=5, pady=5, sticky="n")

        city_label = ctk.CTkLabel(location_frame, text="Enter City:")
        city_label.grid(row=1, column=0, padx=5, pady=5, sticky="n")
        city_input = ctk.CTkEntry(location_frame, placeholder_text="Enter City")
        city_input.grid(row=1, column=1, padx=5, pady=5, sticky="n")

        if self.city:
            city_input.configure(placeholder_text=self.city)
        if self.country:
            country_input.configure(placeholder_text=self.country)

        def save_settings():
            data = {
                "city": city_input.get(),
                "country": country_input.get(),
                "startup_added": True,
            }
            settings_path = get_settings_path()
            try:
                with open(settings_path, "w") as f:
                    json.dump(data, f)
            except Exception as e:
                log.warning("Could not save settings: %s", e)

            self.country = data["country"]
            self.city = data["city"]
            self.prayers_setup()
            self.restart_prayers()
            settings_window.destroy()

        save_btn = ctk.CTkButton(settings_window, text="Save", command=save_settings)
        save_btn.pack(pady=20)

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def draw_borders(self):
        self.main_grid = ctk.CTkFrame(
            self, width=860, height=500, bg_color="transparent", fg_color="transparent"
        )
        self.main_grid.place(relx=0.5, rely=0.5, anchor="center")

        border = Image.open(resource_path("images", "border.png")).resize((860, 500))
        self.border_img = ImageTk.PhotoImage(border)

        self.border_label = ctk.CTkLabel(self.main_grid, image=self.border_img, text="")
        self.border_label.grid(row=0, column=0, sticky="nsew")

        self.circular_grid = ctk.CTkFrame(
            self, width=0, height=0, bg_color="transparent", fg_color="transparent"
        )
        self.circular_grid.place(relx=0.79, rely=0.5, anchor="center")

        circular_border = Image.open(resource_path("images", "circle_border.png"))
        self.circular_border_img = ImageTk.PhotoImage(circular_border)

        self.circular_border_label = ctk.CTkLabel(
            self.circular_grid, image=self.circular_border_img, text=""
        )
        self.circular_border_label.grid(row=0, column=0, padx=0, sticky="")

        circular_border2 = circular_border.resize((195, 195))
        self.circular_border2_img = ImageTk.PhotoImage(circular_border2)

        self.circular_border2_label = ctk.CTkLabel(
            self.circular_grid, image=self.circular_border2_img, text=""
        )
        self.circular_border2_label.grid(row=0, column=0, padx=0, sticky="")

    def label_grid(self):
        self.grid_frame = ctk.CTkFrame(self, width=200, height=100, corner_radius=10)
        self.grid_frame.place(relx=0.05, rely=0.21)

        self.circle_frame = ctk.CTkFrame(
            self,
            width=100,
            height=100,
            corner_radius=10,
            bg_color="transparent",
            fg_color="transparent",
        )
        self.circle_frame.place(relx=0.715, rely=0.43)

        self.title_label = ctk.CTkLabel(
            self.grid_frame, text="Prayer Times", font=("Itim", 36)
        )
        self.title_label.grid(row=0, column=0, padx=80, pady=10, sticky="w", columnspan=2)

        self.fajr_label = ctk.CTkLabel(self.grid_frame, text="Fajr Time: ", font=("IstokWeb", 24))
        self.fajr_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        self.dhuhr_label = ctk.CTkLabel(self.grid_frame, text="Dhuhr Time: ", font=("IstokWeb", 24))
        self.dhuhr_label.grid(row=2, column=0, padx=20, pady=10, sticky="w")
        self.asr_label = ctk.CTkLabel(self.grid_frame, text="Asr Time: ", font=("IstokWeb", 24))
        self.asr_label.grid(row=3, column=0, padx=20, pady=10, sticky="w")
        self.maghrib_label = ctk.CTkLabel(self.grid_frame, text="Maghrib Time: ", font=("IstokWeb", 24))
        self.maghrib_label.grid(row=4, column=0, padx=20, pady=10, sticky="w")
        self.isha_label = ctk.CTkLabel(self.grid_frame, text="Isha Time: ", font=("IstokWeb", 24))
        self.isha_label.grid(row=5, column=0, padx=20, pady=10, sticky="w")

        self.current_time = strftime("%I:%M:%S %p")
        self.current_prayer = None
        self.next_prayer = None

    # ------------------------------------------------------------------
    # Prayer fetching / scheduling
    # ------------------------------------------------------------------

    def _fetch_today_times(self):
        """Try city/country first, fall back to lat/lon. Returns None on failure."""
        try:
            if self.city and self.country:
                return get_prayer_times(self.city, self.country)
        except Exception as e:
            log.warning("get_prayer_times (city) failed: %s", e)

        lat, lon, _, _ = get_location()
        if lat is None:
            return None
        try:
            return get_prayer_times_lat(lat, lon)
        except Exception as e:
            log.warning("get_prayer_times_lat failed: %s", e)
            return None

    def _fetch_tomorrow_times(self):
        try:
            if self.city and self.country:
                return get_tomorrow_prayer_times(self.city, self.country)
        except Exception as e:
            log.warning("get_tomorrow_prayer_times (city) failed: %s", e)

        lat, lon, _, _ = get_location()
        if lat is None:
            return None
        try:
            return get_tomorrow_prayer_times_lat(lat, lon)
        except Exception as e:
            log.warning("get_tomorrow_prayer_times_lat failed: %s", e)
            return None

    def prayers_setup(self):
        self.times = self._fetch_today_times()
        if not self.times:
            log.info("Could not fetch prayer times; will retry on next tick.")
            return

        now = datetime.datetime.now()
        isha_time_str = self.times[PRAYERS.index("Isha")]
        isha_hour, isha_minute = map(int, isha_time_str.split(":"))
        isha_datetime = now.replace(
            hour=isha_hour, minute=isha_minute, second=0, microsecond=0
        )

        if now > isha_datetime:
            tomorrow = self._fetch_tomorrow_times()
            if tomorrow:
                self.times = tomorrow

    def scheduler_setup(self):
        self.prayer_times_list = []
        if not self.times:
            return

        now = datetime.datetime.now()
        for i, (prayer_time, prayer) in enumerate(zip(self.times, PRAYERS), start=1):
            hour, minute = prayer_time.split(":")
            label = ctk.CTkLabel(
                self.grid_frame,
                text=format_12hr(hour, minute),
                font=("IstokWeb", 24),
            )
            label.grid(row=i, column=1, sticky="e", padx=30)
            self.prayer_times_list.append(label)

            run_datetime = now.replace(
                hour=int(hour), minute=int(minute), second=0, microsecond=0
            )
            # Skip prayers that have already passed today — they would
            # otherwise immediately fire as misfires when the scheduler
            # starts. They'll get rescheduled tomorrow via tomorrow_prayers().
            if run_datetime <= now:
                continue

            self.scheduler.add_job(
                self.play_sound_and_show_button,
                "date",
                run_date=run_datetime,
                id=prayer,
                replace_existing=True,
                misfire_grace_time=180,
            )

    def restart_prayers(self):
        self.scheduler.remove_all_jobs()
        for label in self.prayer_times_list:
            label.destroy()
        self.prayer_times_list.clear()
        self.scheduler_setup()

    # ------------------------------------------------------------------
    # Countdown / timer
    # ------------------------------------------------------------------

    def timer(self):
        jobs = self.scheduler.get_jobs()
        if not jobs:
            self.tomorrow_prayers()
            jobs = self.scheduler.get_jobs()

        first_label = jobs[0].id if jobs else "Next prayer"

        self.next_prayer_label = ctk.CTkLabel(
            self.circle_frame,
            text=first_label,
            font=("Itim", 28),
            bg_color="transparent",
        )
        self.next_prayer_label.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")

        self.time_to_prayer = ctk.CTkLabel(
            self.circle_frame,
            text="بِسْمِ ٱللهِ   ",
            font=("Amiri", 36),
            bg_color="transparent",
        )
        self.time_to_prayer.grid(row=1, column=0, padx=0, pady=0, sticky="nsew")

        stop_button_image = PhotoImage(file=resource_path("images", "stop_button.png"))
        stop_button_image = stop_button_image.subsample(3, 3)

        self.overlay_button = ctk.CTkButton(
            self,
            image=stop_button_image,
            text="",
            fg_color="transparent",
            bg_color="transparent",
            hover_color="#333333",
            width=250,
            height=220,
            corner_radius=0,
            command=self.stop,
        )

        self.after(1000, self.update)

    def handle_sleep_resume(self):
        """Drop any jobs whose run time is more than a minute in the past."""
        try:
            self.scheduler.pause()
            self.scheduler.resume()
        except Exception as e:
            log.warning("Scheduler reset failed: %s", e)

        for job in list(self.scheduler.get_jobs()):
            if not job.next_run_time:
                continue
            time_now = datetime.datetime.now(job.next_run_time.tzinfo)
            delay = (time_now - job.next_run_time).total_seconds()
            if delay > 60:
                try:
                    self.scheduler.remove_job(job.id)
                except Exception:
                    pass

    def update(self):
        # Detect long gaps (sleep/resume) before doing anything else.
        time_now_naive = datetime.datetime.now()
        if (time_now_naive - self.last_checked).total_seconds() > 300:
            self.handle_sleep_resume()
        self.last_checked = time_now_naive

        # If the initial fetch failed (e.g. no network at startup, common
        # when launched from Windows login), keep retrying until it works.
        if not self.times:
            self.prayers_setup()
            if self.times:
                self.restart_prayers()

        # Prune any jobs that have already fired but weren't cleaned up.
        jobs = self.scheduler.get_jobs()
        for job in list(jobs):
            if not job.next_run_time:
                continue
            now_tz = datetime.datetime.now(job.next_run_time.tzinfo)
            if job.next_run_time <= now_tz:
                try:
                    self.scheduler.remove_job(job.id)
                except Exception:
                    pass

        # Refresh the list and load tomorrow's if empty.
        jobs = self.scheduler.get_jobs()
        if not jobs:
            self.tomorrow_prayers()
            jobs = self.scheduler.get_jobs()

        if not jobs:
            # Still nothing (network down). Try again next tick.
            self.time_to_prayer.configure(text="--:--:--")
            self.next_prayer_label.configure(text="Unavailable")
            self.after(5000, self.update)
            return

        # Find the actual next prayer by comparing run times.
        next_job = min(jobs, key=lambda j: j.next_run_time)
        run_time = next_job.next_run_time
        self.next_prayer = next_job.id

        now = datetime.datetime.now(run_time.tzinfo)
        diff = max(0, int((run_time - now).total_seconds()))
        mins, secs = divmod(diff, 60)
        hrs, mins = divmod(mins, 60)

        self.time_to_prayer.configure(text=f"{hrs:02}:{mins:02}:{secs:02}")
        self.next_prayer_label.configure(text=next_job.id)

        self.after(1000, self.update)

    def tomorrow_prayers(self):
        times = self._fetch_tomorrow_times()
        if not times:
            return
        self.times = times

        # If labels were never created (e.g. startup network failure meant
        # scheduler_setup ran with self.times=None), build them from scratch
        # via restart_prayers so we have a valid prayer_times_list to update.
        if not self.prayer_times_list:
            self.restart_prayers()
            return

        for i, (prayer_time, prayer) in enumerate(zip(self.times, PRAYERS)):
            hour, minute = map(int, prayer_time.split(":"))
            self.prayer_times_list[i].configure(text=format_12hr(hour, minute))

            run_datetime = (datetime.datetime.now() + timedelta(days=1)).replace(
                hour=hour, minute=minute, second=0, microsecond=0
            )
            self.scheduler.add_job(
                self.play_sound_and_show_button,
                "date",
                run_date=run_datetime,
                id=prayer,
                replace_existing=True,
                misfire_grace_time=180,
            )

    # ------------------------------------------------------------------
    # Adhan playback
    # ------------------------------------------------------------------

    def play_sound_and_show_button(self):
        if not self.winfo_viewable():
            self.deiconify()
            self.lift()
            self.focus_force()

        self.play_sound()
        self.show_button()
        self.after(180000, self.hide_button)

    def hide_button(self):
        self.overlay_button.place_forget()

    def show_button(self):
        self.overlay_button.place(relx=0.79, rely=0.5, anchor="center")

    def play_sound(self):
        if not self.audio_ready:
            return
        try:
            pygame.mixer.music.load(resource_path("audio", "The Adhan - Omar Hisham.mp3"))
            pygame.mixer.music.play(loops=0)
        except Exception as e:
            log.warning("Could not play adhan: %s", e)

    def stop(self):
        if self.audio_ready:
            pygame.mixer.music.stop()
        self.hide_button()


if __name__ == "__main__":
    app = App()
    app.mainloop()