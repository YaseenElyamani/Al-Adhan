import requests
import time
import datetime
PRAYERS = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]


def get_prayer_times(city, country, method=2):
    url = f"https://api.aladhan.com/v1/timingsByCity"
    params = {
        "city": city,
        "country": country,
        "method": method
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()

        fajr_time = data["data"]["timings"]["Fajr"]
        dhuhr_time = data["data"]["timings"]["Dhuhr"]
        asr_time = data["data"]["timings"]["Asr"]
        maghrib_time = data["data"]["timings"]["Maghrib"]
        isha_time = data["data"]["timings"]["Isha"]

        return fajr_time, dhuhr_time, asr_time, maghrib_time, isha_time
    else:
        raise Exception(f"Non-success status code: {response.status_code}")
    
def get_tomrrow_prayer_times(city, country, method=2):
    tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%d-%m-%Y")
    url = f"https://api.aladhan.com/v1/timingsByCity"
    params = {
        "city": city,
        "country": country,
        "method": method,
        "date": tomorrow
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()

        fajr_time = data["data"]["timings"]["Fajr"]
        dhuhr_time = data["data"]["timings"]["Dhuhr"]
        asr_time = data["data"]["timings"]["Asr"]
        maghrib_time = data["data"]["timings"]["Maghrib"]
        isha_time = data["data"]["timings"]["Isha"]

        return fajr_time, dhuhr_time, asr_time, maghrib_time, isha_time
    else:
        raise Exception(f"Non-success status code: {response.status_code}")
    
def get_tomorrow_prayer_times_lat(lat, lon, method=2):
    tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%d-%m-%Y")
    url = "https://api.aladhan.com/v1/timings"
    params = {
        "latitude": lat,
        "longitude": lon,
        "method": method,
        "date": tomorrow
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        fajr_time = data["data"]["timings"]["Fajr"]
        dhuhr_time = data["data"]["timings"]["Dhuhr"]
        asr_time = data["data"]["timings"]["Asr"]
        maghrib_time = data["data"]["timings"]["Maghrib"]
        isha_time = data["data"]["timings"]["Isha"]
        return fajr_time, dhuhr_time, asr_time, maghrib_time, isha_time
    else:
        raise Exception(f"Non-success status code: {response.status_code}")


    
def get_prayer_times_lat(lat, lon, method=2):
    url = f"https://api.aladhan.com/v1/timings"
    params = {
        "latitude": lat,
        "longitude": lon,
        "method": method
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()

        fajr_time = data["data"]["timings"]["Fajr"]
        dhuhr_time = data["data"]["timings"]["Dhuhr"]
        asr_time = data["data"]["timings"]["Asr"]
        maghrib_time = data["data"]["timings"]["Maghrib"]
        isha_time = data["data"]["timings"]["Isha"]

        return fajr_time, dhuhr_time, asr_time, maghrib_time, isha_time
    else:
        raise Exception(f"Non-success status code: {response.status_code}")
    
#Testing purposes only
def print_athan(times):
    print(f"Fajr Time: {times[0]}")
    print(f"Dhuhr Time: {times[1]}")
    print(f"Asr Time: {times[2]}")
    print(f"Maghrib Time: {times[3]}")
    print(f"Isha Time: {times[4]}")

    return
