# Al-Adhan

A lightweight Windows desktop app that displays the five daily Islamic prayer times for your location and plays the adhan (call to prayer) when each prayer time arrives.

## Features

- **Automatic prayer times** for your location, fetched from the [Aladhan API](https://aladhan.com/prayer-times-api)
- **Plays the adhan** at each of the five daily prayer times (Fajr, Dhuhr, Asr, Maghrib, Isha)
- **Live countdown** to the next prayer
- **Manual or automatic location** — enter your city and country, or let the app detect your location by IP
- **Minimizes to system tray** so it stays out of the way; double-click the tray icon to bring the window back
- **Launches at Windows startup** (optional, set during install)
- **Automatically rolls over to the next day** after Isha
- **Handles sleep/resume** — won't fire missed prayers when your laptop wakes up

## Download & Install

1. Go to the [Releases page](../../releases/latest) and download `Al-AdhanSetup.exe`
2. Double-click the installer and follow the wizard
3. The installer will offer optional checkboxes for a desktop icon and launching at Windows startup
4. On first launch, you'll be asked to enter your city and country (you can leave it blank to auto-detect by IP)

### About the SmartScreen warning

The first time you run the installer, Windows will show a warning that says **"Windows protected your PC"**. This is because the app isn't code-signed (signing certificates cost a few hundred dollars per year, which isn't practical for a free personal-use app).

To proceed, click **More info** → **Run anyway**. You can review all the source code in this repository to verify the app does what it claims.

## How it works

When the app starts, it fetches today's prayer times from the [Aladhan API](https://aladhan.com/prayer-times-api) using either your saved city/country or your IP-based location as a fallback. Each prayer time is registered as a scheduled job, and when one fires, the app pops back into view and plays the adhan. After Isha, the app automatically loads tomorrow's times.

Settings and logs are stored in `%APPDATA%\Al-Adhan\` so they persist across reinstalls and updates.

## Building from source

If you'd rather build it yourself instead of using the installer:

### Requirements

- Windows 10 or 11
- Python 3.10+
- The dependencies listed in `requirements.txt`

### Run from source

```bash
git clone https://github.com/yourusername/al-adhan.git
cd al-adhan
python -m pip install -r requirements.txt
python main.py
```

### Build the standalone exe

```bash
python -m pip install pyinstaller
python -m PyInstaller --noconsole --icon=images/logo.ico --add-data "images;images" --add-data "audio;audio" --name "Al-Adhan" main.py
```

The output will be in `dist\Al-Adhan\Al-Adhan.exe`.

### Build the installer

The installer is built with [Inno Setup](https://jrsoftware.org/isdl.php). After building the exe above:

1. Install Inno Setup
2. Open `installer.iss` in the Inno Setup IDE and press **F9** (or right-click the file and choose **Compile**)
3. The installer will be written to `Output\Al-AdhanSetup.exe`

## Project structure

```
al-adhan/
├── main.py              # GUI, scheduler, tray icon, settings
├── prayer.py            # Aladhan API wrapper
├── installer.iss        # Inno Setup installer script
├── requirements.txt
├── images/              # App icons and UI graphics
└── audio/               # Adhan recitation
```

## Troubleshooting

**The app shows "Unavailable" instead of prayer times.**
This usually means the app couldn't reach the Aladhan API at startup (most common when launching at Windows login before the network is fully ready). The app retries automatically every few seconds — give it a minute. If it still doesn't work, check your internet connection.

**Prayer times look wrong.**
The default calculation method is ISNA (Islamic Society of North America). If you're outside North America you may want to use a regional method instead — this isn't currently exposed in the settings UI but is on the roadmap.

**The adhan doesn't play.**
The app falls back to silent mode if your machine has no working audio device. Check `%APPDATA%\Al-Adhan\prayer_times.log` for warnings.

**I want to see what the app is doing.**
The app writes a log to `%APPDATA%\Al-Adhan\prayer_times.log`. Open it in any text editor.

## Acknowledgments

- Prayer times provided by the free [Aladhan API](https://aladhan.com/prayer-times-api)
- Adhan recitation by Omar Hisham

## License

This project is provided as-is for personal use. See `LICENSE` for details.