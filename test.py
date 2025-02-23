from playsound import playsound
import requests
import datetime
import time

playsound()

"""
print(time.ctime(0)) # time expressed in seconds
print(time.time()) # current seconds since epoch
print(time.ctime(time.time())) # Current date and time
"""
time_object = time.localtime() # time object
date = time.strftime("%X", time_object)
print(date)

while (True):
    playsound("WesleyV2.mp3")



for i in range(5, 0, -1):
    print(i)
    print(time.ctime(time.time()))
    time.sleep(1)
    

playsound("The Adhan - Omar Hisham.mp3")
