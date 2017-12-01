import socket
import threading
from queue import Queue
import serial
import matplotlib

from networking import Networker

matplotlib.use("TKAgg")
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
from  matplotlib import style


# Backend things for the GUI

class GUIBackend:
    def __init__(self):
        self.nw = Networker()

    def send_text(self, s):
        self.nw.send(bytes(s, encoding='utf-8'))

    def send_num(self, i):
        self.nw.send(int.to_bytes(i, byteorder='big', length=4))

    def send_byte(self, b):
        """
        Sends a single byte.
        :param b: A number from 0 to 255
        :return: None
        """
        self.nw.send(bytes([b]))

    def connect(self, address, port):
        self.nw.connect(addr=address, port=port)


#######################################

# The GUI frontend


class Plotter:
    def __init__(self, axes, queue_in):
        """
        A class for simplifying plotting:
        :param axes: The axes on which to plot.
        :param queue_in: A queue of new data items that we should plot.
        """
        # TODO make queue_in ints
        self.queue_in = queue_in
        self.xlist = []
        self.ylist = []
        # TODO plot by time instead:
        self.xcnt = 0
        self.axes = axes
        # TODO clear old data.

    def redraw(self):
        self.axes.clear()
        self.axes.plot(self.xlist, self.ylist)

    # animation for live plot
    def animate(self, i):
        if self.queue_in.qsize() > 1:
            first_byte = self.queue_in.get()
            # second_byte = queue1.get()
            pullData = int.from_bytes(first_byte, byteorder="big", signed=True)
            self.xlist.append(self.xcnt)
            self.ylist.append(pullData)
            self.xcnt += 1

        self.redraw()


class GUIFrontend(tk.Tk):

    def __init__(self, backend, *args, **kwargs):
        self.backend = backend

        tk.Tk.__init__(self,*args,**kwargs)

        frame1=tk.Frame(self)
        frame1.pack(side="top", fill="both",expand=True)
        frame1.grid_rowconfigure(0, weight=1)
        frame1.grid_columnconfigure(0, weight=1)

        self.frames={}
        frame=StartPage(frame1,self)
        self.frames['StartPage']=frame
        frame.grid(row=0,column=0,sticky="nesw")
        self.show_frame('StartPage')

        # Setup the animation. FIXME, should this be in the frame?:
        self.animation = animation.FuncAnimation(frame.f,frame.graph1.animate, interval=500)

    def run(self):
        # self.frames[StartPage].updateGui()
        self.mainloop()

    def show_frame(self,cont):
        frame=self.frames[cont]
        frame.tkraise()


# The main frame for the gui.
class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        # configure the plot
        self.f = Figure(figsize=(5, 5), dpi=100)
        a = self.f.add_subplot(111)
        self.graph1 = Plotter(a, Queue())

        tk.Frame.__init__(self,parent)
        label1=tk.Label(self,text="IP")
        label1.grid(row=0,column=10)
        entry2 = tk.Entry(self)
        entry2.grid(row=0, column=11)
        entry2.insert(tk.END, '127.0.0.1')


        label2 = tk.Label(self, text="port")
        label2.grid(row=1, column=10)
        entry3 = tk.Entry(self)
        entry3.insert(tk.END, '1234')
        entry3.grid(row=1, column=11)
        button4 = tk.Button(self, text="Connect",command=lambda:controller.backend.connect(entry2.get(),entry3.get()))
        button4.grid(row=1, column=12)

        #more buttons can be added,as well as text boxes
        #the third arguement is gonna be the function the button need to bind
        button1=tk.Button(self,text="Button1")
        button2 = tk.Button(self, text="Button2")
        button3 = tk.Button(self, text="Button3",command=lambda:controller.backend.send_byte(int(entry1.get())))
        button1.grid(row=100,column=10)
        button2.grid(row=100, column=11)
        button3.grid(row=100, column=12)
        entry1=tk.Entry(self)
        entry1.grid(row=101, column=11)

        #potential for multipage gui
        self.controller=controller

        canvas=FigureCanvasTkAgg(self.f,self)
        canvas.show()
        canvas.get_tk_widget().grid(row=2,column=10,columnspan=3, rowspan=1,padx=5, pady=5,sticky="WENS")

front = GUIFrontend(GUIBackend())

front.run()