import csv
import json
import socket
import threading
from json import JSONDecoder
from queue import Queue

from PIL import ImageTk, Image
from tkinter import PhotoImage
import time
from sklearn import linear_model
import serial
import matplotlib
from scipy import sparse, random
import matplotlib.pyplot as plt
import numpy as np

from concurrency import async
from networking import*

from mk1_gui.server_info import ServerInfo

matplotlib.use("TKAgg")
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
from  matplotlib import style

# Backend things for the GUI

class GUIBackend:
    def __init__(self, queue_out):
        self.nw_queue = Queue()
        self.nw = Networker(queue=self.nw_queue, loglevel=LogLevel.DEBUGV)
        self.queue_out = queue_out
        self.logger = Logger(name='GUI', level=LogLevel.DEBUG, outfile='gui.log')
        self._periodic_process_recv()

    def send_text(self, s):
        self.nw.send(str.encode(s))

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

    @async
    def _periodic_process_recv(self):
        while True:
            time.sleep(0.1)
            if not self.nw.connected:
                continue

            self._process_recv_message()

    def _process_recv_message(self):
        """
        A method that pulls new messages from the nw_queue and processes them and appropriately gives them to
        the GUI thread.
        :return:
        """
        if self.nw_queue.qsize() > 0:
            self.logger.debug("Processing Messages")
        while self.nw_queue.qsize() > 0:
            mtype, nbytes, message = self.nw_queue.get()

            self.logger.debug("Processing message: Type:" + str(mtype) +
                              " Nbytes:" + str(nbytes))

            if mtype == ServerInfo.ACK_VALUE:
                pass
            elif mtype == ServerInfo.PAYLOAD:
                # This means we have a byte array of multiple possible readings from the sensor.
                # First make sure we have a multiple of the size we expect:
                if nbytes % self.nw.server_info.info.payload_bytes != 0:
                    self.logger.error("Received PAYLOAD message with improper number of bytes:" + str(nbytes))
                    return

                # TODO this code is shit.
                self.nw.server_info.read_payload(message, nbytes, self.queue_out)
                # bytes_read = 0
                # while bytes_read < nbytes:
                #     dat = message[bytes_read: bytes_read + payload_bytes]
                #     adc_read = dat[0:payload_bytes]
                #     adc_read = int.from_bytes(adc_read, byteorder=sys.byteorder)
                #     adc_read = socket.ntohs(adc_read)
                #
                #     # TODO use the time to plot stuff
                #     read_time = dat[payload_time_offset:payload_time_offset + payload_bytes]

                #     self.nw.out_queue.put(adc_read)
            elif mtype == ServerInfo.TEXT:
                print(message.decode('utf-8'))
                # sys.stdout.write(message.decode('utf-8'))
            else:
                self.logger.error("Received incorrect message header type")

#######################################

# The GUI frontend
class Plotter:
    def __init__(self, filename, axes, queue_in):
        """
        A class for simplifying plotting:
        :param axes: The axes on which to plot.
        :param queue_in: A queue of new data items that we should plot.
        """
        assert isinstance(queue_in, Queue)

        # TODO make queue_in ints
        self.queue_in = queue_in
        #self.queue_in = [int(q_item) for q_item in queue_in]
        self.xlist = [] #new data to plot on x
        self.ylist = [] #new data to plot on y
        # TODO plot by time instead:
        self.axes = axes
        # TODO clear old data.
        self.filename = filename

    def redraw(self):
        #print ("redrawing")
        self.axes.clear()
        self.axes.plot(self.xlist, self.ylist)

    # animation for live plot
    def animate(self, i):

        if (random.random() > .5):
        #while self.queue_in.qsize() > 1:
            print ("animating")
            # first_byte = self.queue_in.get()
            # # second_byte = queue1.get()
            # pullData = int.from_bytes(first_byte, byteorder="big", signed=True)
            #adc_data, t = self.queue_in.get()

            #self.xlist.append(self.xcnt)
            #self.xlist.append(t) #todo check that x is time
            self.xlist = [x for x in range(10)]
            #self.ylist.append(adc_data)
            self.ylist = [random.random() for x in range(10)]

            #print ("xlist", self.xlist)
            #print ("ylist", self.ylist)

            #append all our input data (what we're plotting on the axes) to a csv file
            #todo
            with open(self.filename, 'a') as save_file:
                writer = csv.writer(save_file, delimiter=" ")
                data = zip(self.xlist, self.ylist)
                for datum in data:
                    writer.writerow(str(datum[0]) + str(datum[1])) #outputs in the format timestamp: data

            self.redraw()

class GUIFrontend(tk.Tk):

    def __init__(self, backend, *args, **kwargs):
        self.backend = backend
        assert isinstance(self.backend, GUIBackend)

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
        self.animation = animation.FuncAnimation(frame.f, frame.graph_60.animate, interval=500)
        self.animation2 = animation.FuncAnimation(frame.f, frame.graph_30.animate, interval=500)
        self.animation3 = animation.FuncAnimation(frame.f, frame.graph_10.animate, interval=500)
        self.animation4 = animation.FuncAnimation(frame.f, frame.graph_1.animate, interval=500)

    def run(self):
        # self.frames[StartPage].updateGui()
        self.mainloop()

    def show_frame(self,cont):
        frame=self.frames[cont]
        frame.tkraise()

# The main frame for the gui.
class StartPage(tk.Frame):
    # calibration values here. Each sensor # is mapped to a tuple containing the y-int and slope for its linear fit
    sensor_calibration = {1: (1, 1), 2: (1, 1), 3: (1, 1), 4: (1, 1), 5: (1, 1), 6: (1, 1), 7: (1, 1), 8: (1, 1)}

    def __init__(self, parent, controller):

        assert isinstance(controller, GUIFrontend)
        # potential for multipage gui
        self.controller=controller

        # configure the plots
        self.f = Figure(figsize=(10, 5), dpi=100)
        #a = self.f.add_subplot(222)
        #self.graph1 = Plotter("main_plot", a, self.controller.backend.queue_out)

        #todo
        #axes = self.f.add_subplot(2)
        #f, (self.graph_60, self.graph_30, self.graph_10, self.graph_1) = plt.subplots(2, 2, sharey=True)
        axes_60 = self.f.add_subplot(221)
        axes_30 = self.f.add_subplot(222)
        axes_10 = self.f.add_subplot(223)
        axes_1 = self.f.add_subplot(224)
        self.graph_60 = Plotter("plot_60", axes_60, self.controller.backend.queue_out)
        self.graph_30 = Plotter("plot_30", axes_30, self.controller.backend.queue_out)
        self.graph_10 = Plotter("plot_10", axes_10, self.controller.backend.queue_out)
        self.graph_1 = Plotter("plot_1", axes_1, self.controller.backend.queue_out)

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
        button1 = tk.Button(self,text="Button1")
        button2 = tk.Button(self, text="send as string", command=lambda:controller.backend.send_text(entry1.get() + "\n"))
        button3 = tk.Button(self, text="send as byte",command=lambda:controller.backend.send_byte(int(entry1.get())))
        button1.grid(row=100,column=10)
        button2.grid(row=100, column=11)
        button3.grid(row=100, column=12)
        entry1=tk.Entry(self)
        entry1.grid(row=101, column=11)

        #the buttons for actuating the single valve
        button5 = tk.Button(self, text="Set Valve",command=lambda:controller.backend.send_byte(ServerInfo.SET_VALVE))
        button6 = tk.Button(self, text="Unset Valve", command=lambda:controller.backend.send_byte(ServerInfo.UNSET_VALVE))

        button5.grid(row=105, column = 10)
        button6.grid(row=105, column=11)

        #Calibration buttons and fields
        entry4 = tk.Entry(self)

        #Input a single int representing the sensor #
        button7 = tk.Button(self, text="Load Calibration", command=lambda:self.load_calibration(entry4.get))
        # Input 2n + 1 numbers: sensor # and n ordered pairs, all comma separated
        button8 = tk.Button(self, text="Set Calibration", command=lambda: self.set_calibration(entry4.get()))

        button7.grid(row=108, column=11)
        button8.grid(row=108, column=12)

        #Disconnect button
        button9 = tk.Button(self, text="Disconnect", command=lambda:controller.backend.disconnect())
        button9.grid(row=108, column=10)

        nutButton = PhotoImage(file="nut.png")
        label = tk.Label(image=nutButton)
        label.image = nutButton
        label.place(relx=.5, rely=.5)

        canvas=FigureCanvasTkAgg(self.f, self)
        canvas.show()
        canvas.get_tk_widget().grid(row=2,column=10,columnspan=3, rowspan=1,padx=5, pady=5,sticky="WENS")

    #todo should probably reverse these and just save y-int and slope instead of saving all the points
    def load_calibration(self, input):
        file = open('calibration.txt', 'r')
        # read in the JSON object that has sensor # mapped to another json object mapping x to y
        calibration_json = json.loads(file.read())

        #first two in input is the sensor #
        #get a dict from the json object mapped to sensor #
        sensor_num = int(input[0:1])
        data = json.loads(calibration_json[sensor_num])

        regr = linear_model.LinearRegression()
        regr.fit(data.keys(), data.values())

        self.sensor_calibration[sensor_num] = (regr.intercept_, regr.coef_)

        file.close()

    def set_calibration(self, input):
        values = input.split(",")
        sensor_num = int(values[0])
        x_values = []
        y_values = []

        for i in range(1, len(values)):
            if i % 2 == 1:
                x_values.append(int(values[i]))
            else:
                y_values.append(int(values[i]))

        self.sensor_calibration[sensor_num] = dict(zip(x_values, y_values))

        file = open('calibration.txt', 'w')
        file.write(json.dumps(self.sensor_calibration))

        #Save it to file then load it.
        self.load_calibration(sensor_num)
        file.close()

front = GUIFrontend(GUIBackend(Queue()))
front.run()