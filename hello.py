from tkinter import *

root = Tk()

"""
e = Entry(root, width=50, bg="blue", fg="white", borderwidth=5)
e.pack()

def myClick():
    myLabel3 = Label(root, text="Good clicking soldier!")
    myLabel3.pack()

#Creating a text/Label widget
myLabel = Label(root, text="Hello World!")
myLabel2 = Label(root, text="My name is Yaseen Elyamani")
myButton = Button(root, text="Click Me!", command=myClick, fg="blue", bg="red")
#Shoving it onto the screen

myButton.pack()
#myLabel.pack()
#myLabel2.pack()
root.mainloop()
"""

e = Entry(root, width= 50)
e.pack()
e.insert(0, "Enter your name:")

def myClick():
    myLabel = Label(root, text="Hello " + e.get())
    myLabel.pack()

myButton = Button(root, text="Enter your Name", command=myClick)
myButton.pack()

root.mainloop()