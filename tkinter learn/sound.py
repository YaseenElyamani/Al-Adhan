from tkinter import *
import pygame

root = Tk()

root.title('Soundplayer')
root.geometry('500x400')

pygame.mixer.init()

def play():
    pygame.mixer.music.load("audio/quran1.mp3")
    pygame.mixer.music.play(loops=5)

def stop():
    pygame.mixer.music.stop()

my_button = Button(root, text="Play Song", font=("Helvetica", 32), command=play)
my_button.pack(pady=20)

stop_button = Button(root, text="Stop", command=stop)
stop_button.pack(pady=20)

root.mainloop()