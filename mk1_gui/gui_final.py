from collections import deque
from tkinter import PhotoImage
from scipy import random
import tkinter as tk
from concurrency import async
from networking import*
import matplotlib.animation as animation
from server_info import ServerInfo
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib
matplotlib.use('TkAgg')


class GUIBackend:
    def __init__(self, queue_lc1s, queue_lc2s, queue_lc3s, queue_lc_mains, queue_tc1s, queue_tc2s, queue_tc3s,
                 queue_feeds, queue_injes, queue_combs):

        self.nw_queue = Queue()
        self.nw = Networker(queue=self.nw_queue, loglevel=LogLevel.INFO)

        self.Q_LC1S = queue_lc1s
        self.Q_LC2S = queue_lc2s
        self.Q_LC3S = queue_lc3s
        self.Q_LCMAINS = queue_lc_mains

        self.Q_TC1S = queue_tc1s
        self.Q_TC2S = queue_tc2s
        self.Q_TC3S = queue_tc3s

        self.Q_FEEDS = queue_feeds
        self.Q_INJES = queue_injes
        self.Q_COMBS = queue_combs

        # A dictionary to match received info to queues (see _process_recv_message)
        self.queue_dict = {
            ServerInfo.LC1S: self.Q_LC1S,
            ServerInfo.LC2S: self.Q_LC2S,
            ServerInfo.LC3S: self.Q_LC3S,
            ServerInfo.LC_MAINS: self.Q_LCMAINS,
            ServerInfo.TC1S: self.Q_TC1S,
            ServerInfo.TC2S: self.Q_TC2S,
            ServerInfo.TC3S: self.Q_TC3S,
            ServerInfo.PT_FEEDS: self.Q_FEEDS,
            ServerInfo.PT_COMBS: self.Q_COMBS,
            ServerInfo.PT_INJES: self.Q_INJES
        }

        self.logger = Logger(name='GUI', level=LogLevel.INFO, outfile='gui.log')
        self._periodic_process_recv()

    def send_text(self, s):
        self.nw.send(str.encode(s))

    def send_num(self, i):
        self.nw.send(int.to_bytes(i, byteorder='big', length=4))

    def send_byte(self, b):
        self.nw.send(bytes([b]))

    def send(self, b):
        self.nw.send(b)

    def connect(self, address, port):
        self.nw.connect(addr=address, port=port)

    def ignite(self):
        self.nw.send(ServerInfo.NORM_IGNITE)

    @async
    def _periodic_process_recv(self):
        while True:
            time.sleep(0.1)
            if not self.nw.connected:
                continue

            self._process_recv_message()

    def _process_recv_message(self):
        """
        Processes new messages from nw_queue and give them to the appropriate GUI thread.
        """
        if self.nw_queue.qsize() > 0:
            self.logger.debug("Processing Messages")

        while self.nw_queue.qsize() > 0:
            mtype, nbytes, message = self.nw_queue.get()
            self.logger.debug("Processing message: Type:" + str(mtype) + " Nbytes:" + str(nbytes))

            # If the data size isn't what we expect, do nothing
            if nbytes % self.nw.server_info.info.payload_bytes != 0:
                self.logger.error("Received PAYLOAD message with improper number of bytes:" + str(nbytes))
                return
            else: # Check mtype to determine what to do
                if mtype == ServerInfo.ACK_VALUE:
                    pass
                elif mtype in ServerInfo.filenames.keys():
                    self.nw.server_info.read_payload(message, nbytes, self.queue_dict[mtype], mtype)
                elif mtype == ServerInfo.TEXT:
                    print(message.decode('utf-8'))
                    # sys.stdout.write(message.decode('utf-8'))
                else:
                    self.logger.error("Received incorrect message header type" + str(mtype))


class Plotter:
    def __init__(self, name, xlabel, ylabel, axes, queue_in, data_length):

        self.queue_in = queue_in
        self.data_length = data_length
        self.xlist = deque(maxlen=data_length)  # new data to plot on x
        self.xlist.append(0)
        self.ylist = deque(maxlen=data_length)  # new data to plot on y
        self.ylist.append(0)
        self.axes = axes

        self.name = name
        self.xlabel = xlabel
        self.ylabel = ylabel

    def redraw(self):
        # Clearing is slow but we don't have to manually rescale axes this way
        self.axes.cla()

        # Resetting the axes titles every time is annoying
        self.axes.set_title(self.name)
        self.axes.set_xlabel(self.xlabel)
        self.axes.set_ylabel(self.ylabel)
        self.axes.plot(self.xlist, self.ylist)

    def animate(self, *fargs):

        # Randomly generate some data to plot
        for i in range(10):
            self.queue_in.put((i, self.xlist[-1] + i))

        while self.queue_in.qsize() > 1:
            adc_data, t = self.queue_in.get()

            self.xlist.append(t)
            self.ylist.append(adc_data)

            # print ("xlist", self.xlist)
            # print ("ylist", self.ylist)
            # print (self.filename, "Avg of last 5 values: ", sum(self.ylist[-5:])/5.0)
        self.redraw()


class GUIFrontend():

    def __init__(self, backend):
        self.backend = backend
        self.root = tk.Tk()
        self.root.resizable(False, False)
        self.root.wm_title("Rice Eclipse Mk-1.1 GUI")

        # This figure contains everything to do with matplotlib on the left hand side
        self.figure = Figure(figsize=(8, 6), dpi=100)

        canvas = FigureCanvasTkAgg(self.figure, master=self.root)
        canvas.get_tk_widget().grid(row=1, column=1, sticky="NW")
        canvas.show()

        # Create 4 graphs in a 2 by 2 grid
        top_left = self.figure.add_subplot(221)
        top_right = self.figure.add_subplot(222)
        bot_left = self.figure.add_subplot(223)
        bot_right = self.figure.add_subplot(224)
        self.figure.subplots_adjust(top=.9, bottom=.1, left=.08, right=.95, wspace=.3, hspace=.5)

        # Configure the plotters for matplotlib
        self.top_left = Plotter("Load Cell 1", "Time (ms)", "Force (N)", top_left, self.backend.Q_LC1S, 100)
        self.top_right = Plotter("Load Cell 2", "Time (ms)", "Force (N)", top_right, self.backend.Q_LC2S, 50)
        self.bot_left = Plotter("PT Feed", "Time (ms)", "Pressure (PSI)", bot_left, self.backend.Q_FEEDS, 25)
        self.bot_right = Plotter("Thermocouple 2", "Time (ms)", "Temperature (C)", bot_right, self.backend.Q_TC2S, 10)

        self.top_left_anim = animation.FuncAnimation(self.figure, self.top_left.animate, interval=100)
        self.top_right_anim = animation.FuncAnimation(self.figure, self.top_right.animate, interval=100)
        self.bot_left_anim = animation.FuncAnimation(self.figure, self.bot_left.animate, interval=100)
        self.bot_right_anim = animation.FuncAnimation(self.figure, self.bot_right.animate, interval=100)

        # This frame contains everything to do with buttons and entry boxes on the right hand side
        # TODO there's plenty of space left over for stuff like calibration, ignite time, etc.
        frame = tk.Frame(background="AliceBlue", width=350, height=600)
        frame.grid(row=1, column=2, sticky="NE")

        ip_label = tk.Label(frame, text="IP", background="AliceBlue")
        ip_label.place(relx=.15, rely=.05)

        ip_entry = tk.Entry(frame)
        ip_entry.config(width=15)
        ip_entry.place(relx=.2, rely=.05)
        ip_entry.insert(tk.END, '192.168.1.137')

        port_label = tk.Label(frame, text="port", background="AliceBlue")
        port_label.place(relx=.6, rely=.05)

        port_entry = tk.Entry(frame)
        port_entry.config(width=5)
        port_entry.insert(tk.END, '1234')
        port_entry.place(relx=.7, rely=.05)

        # Connect and disconnect buttons
        connect_button = tk.Button(frame, text="Connect",
                                   command=lambda:backend.connect(ip_entry.get(), port_entry.get()))
        connect_button.place(relx=.25, rely=.1)

        disconnect_button = tk.Button(frame, text="Disconnect",
                                      command=lambda:backend.nw.disconnect())
        disconnect_button.place(relx=.6, rely=.1)

        # Buttons for actuating the valve
        set_valve_button = tk.Button(frame, text="Set Valve",
                            command=lambda:backend.send(ServerInfo.SET_VALVE))
        unset_valve_button = tk.Button(frame, text="Unset Valve",
                            command=lambda:backend.send(ServerInfo.UNSET_VALVE))

        set_valve_button.place(relx=.25, rely=.45)
        unset_valve_button.place(relx=.5, rely=.45)

        set_ignition_button = tk.Button(frame, text="IGNITE",
                                        command=lambda:backend.send(ServerInfo.SET_IGNITION))
        set_ignition_image = PhotoImage(file="ignite.gif")
        set_ignition_button.config(image=set_ignition_image)
        set_ignition_button.image = set_ignition_image
        set_ignition_button.place(relx=.15, rely=.75)

        unset_ignition_button = tk.Button(frame, text="UNIGNITE",
                                          command=lambda: backend.send(ServerInfo.UNSET_IGNITION))
        unset_ignition_image = PhotoImage(file="unignite.gif")
        unset_ignition_button.config(image=unset_ignition_image)
        unset_ignition_button.image = unset_ignition_image
        unset_ignition_button.place(relx=.55, rely=.75)

frontend = GUIFrontend(GUIBackend(Queue(), Queue(), Queue(), Queue(), Queue(),
                                  Queue(), Queue(), Queue(), Queue(), Queue()))
frontend.root.mainloop()