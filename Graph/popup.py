from tkinter import *


class PopUp:
    def __init__(self):
        self.window = None
        self.txt = None
        self.weight = 0

    def pop(self):
        self.window = Tk()

        self.window.title("Edge Weight")

        self.window.geometry('300x50')

        # add label
        label = Label(self.window, text="Enter weight")
        label.grid(column=0, row=10)

        # add entry
        self.txt = Entry(self.window, width=10)
        self.txt.grid(column=1, row=10)

        # add button
        btn = Button(self.window, text="Add Edge", command=self.clicked)
        btn.grid(column=2, row=10)

        self.window.mainloop()

    def clicked(self):
        try:
            self.weight = float(self.txt.get())
            print(self.weight)
            self.window.destroy()
        except AttributeError as e:
            print("Enter a valid float")
