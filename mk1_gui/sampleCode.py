import matplotlib
matplotlib.use('TkAgg')

from numpy import arange, sin, pi
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import tkinter as Tk

root = Tk.Tk()
root.wm_title("Rice Eclipse Mk-1.1 GUI")

figure = Figure(figsize=(8, 6), dpi=100)

# Create 4 graphs in a 2 by 2 grid
top_left = figure.add_subplot(221)
top_left.set_title("abcd")
top_right = figure.add_subplot(222)
bot_left = figure.add_subplot(223)
bot_right = figure.add_subplot(224)
figure.subplots_adjust(top = .9, bottom=.1, left=.08, right = .95, wspace=.2, hspace=.5)

# generate some dummy data
t = arange(0.0, 3.0, 0.01)
s = sin(2*pi*t)

top_left.plot(t, s)

# a tk.DrawingArea
canvas = FigureCanvasTkAgg(figure, master=root)
canvas.get_tk_widget().grid(row=1, column=1, sticky="NW")
canvas.show()

background_frame = Tk.Frame(background = "bisque", width=350, height=600)
background_frame.grid(row=1, column=2, sticky="NE")

Tk.mainloop()