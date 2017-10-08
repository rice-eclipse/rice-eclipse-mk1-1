#right now only one plot is gonna be displayed; just add more if necessary


import socket
import threading
from queue import Queue
import serial
import matplotlib
matplotlib.use("TKAgg")
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
from  matplotlib import style
s = socket.socket()

#make it configurable in the gui (text input box and button)


#data buffer
queue1 = Queue()
x_index= Queue()
x_index.put(0)


#plot style
style.use("dark_background")

#configure the plot
f = Figure(figsize=(5, 5), dpi=100)
a = f.add_subplot(111)
xlist = []
ylist = []



#animation for live plot
def animate(i):
    if queue1.qsize()>1:
        first_byte = queue1.get()
        #second_byte = queue1.get()
        pullData = int.from_bytes(first_byte, byteorder="big", signed=True)
        index=x_index.get()
        xlist.append(index)
        ylist.append(pullData)
        index=index+1
        x_index.put(index)
        a.clear()
        a.plot(xlist,ylist)
    else:
        a.plot(xlist, ylist)




# called serialread, actually socket read though. rename if you want (be sure to change the name in other locations)
# change the argument in recv to change number of bytes receive at a time
def serialread(s, q):
    while 1:
        data = s.recv(2)
        if len(data) != 0:
            q.put(data)



# thread for data acquisition
class myThread1(threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def run(self):
        serialread(s, queue1)



#gui set up
class gui(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self,*args,**kwargs)

        frame1=tk.Frame(self)
        frame1.pack(side="top", fill="both",expand=True)
        frame1.grid_rowconfigure(0, weight=1)
        frame1.grid_columnconfigure(0, weight=1)

        self.frames={}
        frame=StartPage(frame1,self)
        self.frames[StartPage]=frame
        frame.grid(row=0,column=0,sticky="nesw")
        self.show_frame(StartPage)
    def run(self):
        # self.frames[StartPage].updateGui()
        self.mainloop()
    def show_frame(self,cont):
        frame=self.frames[cont]
        frame.tkraise()

#function to connect the socket
def connect_socket(host,port):
    s.connect((host, int(port)))

# test function for sending via socket
def test(entry):
    s.send(str.encode(entry))
    s.send(str.encode("\n"))



# startpage
class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        label1=tk.Label(self,text="IP")
        label1.grid(row=0,column=10)
        entry2 = tk.Entry(self)
        entry2.grid(row=0, column=11)

        label2 = tk.Label(self, text="port")
        label2.grid(row=1, column=10)
        entry3 = tk.Entry(self)
        entry3.grid(row=1, column=11)
        button4 = tk.Button(self, text="Connect",command=lambda:connect_socket(entry2.get(),entry3.get()))
        button4.grid(row=1, column=12)

        #more buttons can be added,as well as text boxes
        #the third arguement is gonna be the function the button need to bind
        button1=tk.Button(self,text="Button1")
        button2 = tk.Button(self, text="Button2")
        button3 = tk.Button(self, text="Button3",command=lambda:test(entry1.get()))
        button1.grid(row=100,column=10)
        button2.grid(row=100, column=11)
        button3.grid(row=100, column=12)
        entry1=tk.Entry(self)
        entry1.grid(row=101, column=11)

        #potential for multipage gui
        self.controller=controller

        canvas=FigureCanvasTkAgg(f,self)
        canvas.show()
        canvas.get_tk_widget().grid(row=2,column=10,columnspan=3, rowspan=1,padx=5, pady=5,sticky="WENS")


    # don't actually need it right now
    # def updateGui(self):
    #     if queue1.qsize() >= 2:
    #         first_byte = queue1.get()
    #         second_byte = queue1.get()
    #
    #         final_num = int.from_bytes(second_byte+first_byte, byteorder="big",signed=True)
    #         self.controller.lbl["text"] = final_num
    #         self.controller.update()
    #         self.controller.lbl.after(1000, self.updateGui)
    #     else:
    #         self.controller.lbl.after(1000, self.updateGui)

gui1=gui()

#put the thread run in a button binded function in order to control when it would run

#uncoment to receive the data in 2byte per int mode
#thread1 = myThread1(1, "Thread-1", 1)
#thread1.start()
ani=animation.FuncAnimation(f,animate,interval=500)

gui1.run()
