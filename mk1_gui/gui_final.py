import csv
import json
from tkinter import PhotoImage
import time
from sklearn import linear_model
import matplotlib
from scipy import random
import tkinter as tk
from concurrency import async
from networking import*
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
from mk1_gui.server_info import ServerInfo

matplotlib.use("TKAgg")
# Backend things for the GUI


class GUIBackend:
    def __init__(self, queue_lcm, queue_lc1, queue_lc2, queue_lc3, queue_pt1, queue_pt2, queue_pt3,
                 queue_tc1, queue_tc2, queue_tc3):
        self.nw_queue = Queue()
        self.nw = Networker(queue=self.nw_queue, loglevel=LogLevel.DEBUGV)
        self.queue_lcm = queue_lcm
        self.queue_lc1 = queue_lc1
        self.queue_lc2 = queue_lc2
        self.queue_lc3 = queue_lc3
        self.queue_pt1 = queue_pt1
        self.queue_pt2 = queue_pt2
        self.queue_pt3 = queue_pt3
        self.queue_tc1 = queue_tc1
        self.queue_tc2 = queue_tc2
        self.queue_tc3 = queue_tc3

        self.logger = Logger(name='GUI', level=LogLevel.DEBUG, outfile='gui.log')
        self._periodic_process_recv()

    def send_text(self, s):
        self.nw.send(str.encode(s))

    def send_num(self, i):
        self.nw.send(int.to_bytes(i, byteorder='big', length=4))

    def send_byte(self, b):
        """
        Sends a single byte from 0 to 255
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
        Pulls/processes new messages from the nw_queue and gives them to the appropriate GUI thread.
        :return:
        """
        # print("nw_queue size", self.nw_queue.qsize())

        if self.nw_queue.qsize() > 0:
            self.logger.debug("Processing Messages")
        while self.nw_queue.qsize() > 0:
            mtype, nbytes, message = self.nw_queue.get()
            # self.logger.debug("Processing message: Type:" + str(mtype) +" Nbytes:" + str(nbytes))

            # print("Mtype", str(mtype), str(ServerInfo.LC1S), type(mtype), type(ServerInfo.LC1S), type(ServerInfo.LC1S[0]), mtype==ServerInfo.LC1S[0])
            # todo add multiple payload outputs
            if mtype == ServerInfo.ACK_VALUE[0]:
                pass

            elif mtype == ServerInfo.LC_MAINS[0]:
                # print("Equal to LC1S")
                if nbytes % self.nw.server_info.info.payload_bytes != 0:
                    self.logger.error("Received PAYLOAD message with improper number of bytes:" + str(nbytes))
                # print("Returned from LC1S")
                return self.nw.server_info.read_payload(message, nbytes, self.queue_lcm)
            elif mtype == ServerInfo.LC1S[0]:
                return self.nw.server_info.read_payload(message, nbytes, self.queue_lc1)
            elif mtype == ServerInfo.LC2S[0]:
                return self.nw.server_info.read_payload(message, nbytes, self.queue_lc2)
            elif mtype == ServerInfo.LC3S[0]:
                return self.nw.server_info.read_payload(message, nbytes, self.queue_lc3)

            elif mtype == ServerInfo.TC1S[0]:
                return self.nw.server_info.read_payload(message, nbytes, self.queue_tc1)
            elif mtype == ServerInfo.TC2S[0]:
                return self.nw.server_info.read_payload(message, nbytes, self.queue_tc2)
            elif mtype == ServerInfo.TC3S[0]:
                return self.nw.server_info.read_payload(message, nbytes, self.queue_tc3)

            elif mtype == ServerInfo.PT_COMBS[0]:
                return self.nw.server_info.read_payload(message, nbytes, self.queue_pt1)
            elif mtype == ServerInfo.PT_FEEDS[0]:
                return self.nw.server_info.read_payload(message, nbytes, self.queue_pt2)
            elif mtype == ServerInfo.PT_INJES[0]:
                return self.nw.server_info.read_payload(message, nbytes, self.queue_pt3)

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
            elif mtype == ServerInfo.TEXT[0]:
                print(message.decode('utf-8'))
                # sys.stdout.write(message.decode('utf-8'))
            else:
                self.logger.error("Received incorrect message header type")

#######################################

# The Plotter for our data display


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
        # self.queue_in = [int(q_item) for q_item in queue_in]
        self.xlist = []  # new data to plot on x
        self.ylist = []  # new data to plot on y
        # TODO plot by time instead:
        self.axes = axes
        # TODO clear old data.
        self.filename = filename

    def redraw(self):
        #print ("redrawing")
        self.axes.clear()
        self.axes.plot(self.xlist, self.ylist)

    def log(self):
        # log all our input data (what we're plotting on the axes) to a csv file
        with open(self.filename, 'a') as save_file:  # append
            writer = csv.writer(save_file, delimiter=" ")
            data = zip(self.xlist, self.ylist)
            for datum in data:
                writer.writerow(str(datum[0]) + str(datum[1]))  # outputs in the format timestamp: data

    def animate(self, i):
         while self.queue_in.qsize() > 1:
            #print ("animating")
            adc_data, t = self.queue_in.get()
            self.xlist.append(t) #todo check that x is time
            self.ylist.append(adc_data)

            #print ("xlist", self.xlist)
            #print ("ylist", self.ylist)

         print(self.filename, "Avg of last 5 values: ", sum(self.ylist[-5:]) / 5.0)
         self.log()
         #print("y-list", self.ylist)
         self.redraw()



# A front end that handles buttons and drawings. Has an associated backend.


class GUIFrontend(tk.Tk):

    def __init__(self, backend, *args, **kwargs):
        self.backend = backend
        self.plotters = []

        tk.Tk.__init__(self,*args,**kwargs)

        background_frame = tk.Frame(self, width=1280, height=800)
        background_frame.pack(side="top", fill="both", expand=True)
        background_frame.grid_rowconfigure(0, weight=1)
        background_frame.grid_columnconfigure(0, weight=1)

        # todo is background_frame necessary here?
        self.frames = {}
        frame = StartPage(background_frame, self)
        self.frames['StartPage'] = frame
        frame.grid(row=0, column=0, sticky="nesw")
        self.show_frame('StartPage')

        # Setup the animation. FIXME, should this be in the frame?:
        # I'm disgusted that this works.
        #self.anim_60 = animation.FuncAnimation(frame.figure, frame.graph1.animate, interval=500)
        #self.anim_30 = animation.FuncAnimation(frame.figure, frame.graph2.animate, interval=500)
        self.anim_10 = animation.FuncAnimation(frame.figure, frame.graph3.animate, interval=500)
        #self.anim_1 = animation.FuncAnimation(frame.figure, frame.graph4.animate, interval=500)

        # todo make this cleaner
        self.plotters = [frame.graph1, frame.graph2, frame.graph3, frame.graph4,
                         frame.pt1, frame.pt2, frame.pt3,
                         frame.tc1, frame.tc2, frame.tc3]

        for plot in self.plotters:
            plot.log()


    def run(self):
        self.mainloop()

    def show_frame(self,cont):
        frame=self.frames[cont]
        frame.tkraise()

# The main frame for the gui.


class StartPage(tk.Frame):
    # Initial calibration values. Each sensor # is mapped to a tuple containing the y-int and slope for its linear fit
    sensor_calibration = {1: (1, 1), 2: (1, 1),
                          3: (1, 1), 4: (1, 1),
                          5: (1, 1), 6: (1, 1),
                          7: (1, 1), 8: (1, 1)}

    def __init__(self, parent, controller):

        assert isinstance(controller, GUIFrontend)
        # Potential for multi-page gui
        self.controller=controller

        # Configure the plots
        # todo
        self.figure = Figure(figsize=(10, 5), dpi=100)
        col_count, row_count = controller.grid_size()
        for col in range(col_count):
            controller.grid_columnconfigure(col, minsize = 10)

        # Create 4 graphs in a 2 by 2 grid
        axes1 = self.figure.add_subplot(221)
        axes2 = self.figure.add_subplot(222)
        axes3 = self.figure.add_subplot(223)
        axes4 = self.figure.add_subplot(224)
        # add axes selection for plots
        self.graph1 = Plotter("adc1", axes1, self.controller.backend.queue_pt1)
        self.graph2 = Plotter("adc2", axes2, self.controller.backend.queue_pt2)
        self.graph3 = Plotter("tc1", axes3, self.controller.backend.queue_tc1)
        self.graph4 = Plotter("lcm", axes4, self.controller.backend.queue_lcm)

        # axes don't matter since we won't be animating these plots
        self.pt1 = Plotter("adc1", axes1, self.controller.backend.queue_lc1)
        self.pt2 = Plotter("adc2", axes1, self.controller.backend.queue_lc2)
        self.pt3 = Plotter("adc3", axes1, self.controller.backend.queue_lc3)
        self.tc1 = Plotter("plot_1", axes1, self.controller.backend.queue_tc1)
        self.tc2 = Plotter("adc1", axes1, self.controller.backend.queue_tc2)
        self.tc3 = Plotter("adc2", axes1, self.controller.backend.queue_tc3)

        tk.Frame.__init__(self, parent)
        ip_label = tk.Label(self, text="IP")
        ip_label.place(relx=.25, rely=0)
        ip_entry = tk.Entry(self)
        ip_entry.place(relx=.3, rely=0)
        ip_entry.insert(tk.END, '127.0.0.1')

        port_label = tk.Label(self, text="port")
        port_label.place(relx=.7, rely=0)
        port_entry = tk.Entry(self)
        port_entry.insert(tk.END, '1234')
        port_entry.place(relx=.75, rely=0)

        # Connect and disconnect buttons
        connect_button = tk.Button(self, text="Connect", command=lambda: controller.backend.connect(ip_entry.get(), port_entry.get()))
        connect_button.grid(row=1, column=11)

        disconnect_button = tk.Button(self, text="Disconnect",
                                      command=lambda: controller.backend.disconnect())
        disconnect_button.place(relx=.9, rely=0)

        send_string_button = tk.Button(self, text="send as string",
                            command=lambda:controller.backend.send_text(send_entry.get() + "\n"))
        send_byte_button = tk.Button(self, text="send as byte",
                            command=lambda:controller.backend.send_byte(int(send_entry.get())))
        send_string_button.grid(row=3, column = 10)
        send_byte_button.grid(row=3, column = 12)

        send_entry = tk.Entry(self)
        send_entry.grid(row=3, column = 11)

        # Buttons for actuating the valve
        set_valve_button = tk.Button(self, text="Set Valve",
                            command=lambda:controller.backend.send_byte(ServerInfo.SET_VALVE))
        unset_valve_button = tk.Button(self, text="Unset Valve",
                            command=lambda:controller.backend.send_byte(ServerInfo.UNSET_VALVE))

        set_valve_button.grid(row=5, column = 11)
        unset_valve_button.grid(row=5, column = 12)

        # Calibration buttons and entry boxes
        calibration_entry = tk.Entry(self)
        calibration_entry.grid(row=4, column = 11)

        # Input a single int representing the sensor #
        load_calibration_button = tk.Button(self, text="Load Calibration",
                                            command=lambda:self.load_calibration(calibration_entry.get))
        # Input 2n + 1 numbers: sensor # and n xy-pairs, all comma separated
        set_calibration_button = tk.Button(self, text="Set Calibration",
                                           command=lambda: self.set_calibration(calibration_entry.get()))

        load_calibration_button.grid(row=4, column = 10)
        set_calibration_button.grid(row=4, column = 12)

        # todo ignition button
        set_ignition_button = tk.Button(self,
                                        command=lambda:controller.backend.send_byte(ServerInfo.SET_IGNITION))
        set_ignition_image = PhotoImage(file="nut.png")
        set_ignition_button.config(image=set_ignition_image)
        set_ignition_button.image = set_ignition_image
        set_ignition_button.grid(row=115, column=11)

        unset_ignition_button = tk.Button(self,
                                          command=lambda: controller.backend.send_byte(ServerInfo.UNSET_IGNITION))
        unset_ignition_image = PhotoImage(file="abort.gif")
        unset_ignition_button.config(image=unset_ignition_image)
        unset_ignition_button.image = unset_ignition_image
        unset_ignition_button.grid(row=115, column=5)

        # This configures where the graphs are on the canvas
        canvas = FigureCanvasTkAgg(self.figure, self)
        canvas.show()
        # todo configure these
        canvas.get_tk_widget().grid(row=2, column=10, columnspan=3, rowspan=1, padx=5, pady=5, sticky="WENS")

    # todo now that we have calibration, actually use it when plotting
    def load_calibration(self, input):
        file = open('calibration.txt', 'r')

        # Read in the JSON object that has sensor # mapped to another json object mapping x to y
        calibration_json = json.loads(file.read())

        # First input is the sensor #
        # Update the calibration based on the value in the json object
        sensor_num = int(input[0:1])
        data = json.loads(calibration_json[sensor_num])
        self.sensor_calibration[sensor_num] = data

        file.close()

    def set_calibration(self, input):
        values = input.split(",")
        sensor_num = int(values[0])
        x_values = [int(values[i]) for i in range(1, len(values)) if i % 2 == 1]
        y_values = [int(values[i]) for i in range(1, len(values)) if i % 2 == 0]

        # Fit the data and update the calibration
        regr = linear_model.LinearRegression()
        regr.fit(x_values, y_values)
        self.sensor_calibration[sensor_num] = (regr.intercept_, regr.coef_)

        # Save the calibration to file
        file = open('calibration.txt', 'w')
        file.write(json.dumps(self.sensor_calibration))
        file.close()


frontend = GUIFrontend(GUIBackend(Queue(), Queue(), Queue(), Queue(),
                                  Queue(), Queue(), Queue(), Queue(),
                                  Queue(), Queue()))
frontend.run()