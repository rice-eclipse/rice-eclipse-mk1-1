from collections import deque
from tkinter import PhotoImage
import matplotlib.pyplot as plt
from scipy import random
import tkinter as tk
import math
from tkinter import scrolledtext
import Pmw
import tkinter.ttk as ttk
from concurrency import async
from networking import*
import matplotlib.animation as animation
from server_info import ServerInfo
from graph_constants import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use('TkAgg')


class GUIBackend:
    def __init__(self, queue_lc1s, queue_lc2s, queue_lc3s, queue_lc_main, queue_tc1s, queue_tc2s, queue_tc3s,
                 queue_feed, queue_inje, queue_comb):

        self.nw_queue = Queue()
        self.nw = Networker(queue=self.nw_queue, loglevel=LogLevel.INFO)

        self.Q_LC1S = queue_lc1s
        self.Q_LC2S = queue_lc2s
        self.Q_LC3S = queue_lc3s
        self.Q_LCMAIN = queue_lc_main

        self.Q_TC1S = queue_tc1s
        self.Q_TC2S = queue_tc2s
        self.Q_TC3S = queue_tc3s

        self.Q_FEED = queue_feed
        self.Q_INJE = queue_inje
        self.Q_COMB = queue_comb

        self.queues = [self.Q_LC1S, self.Q_LC2S, self.Q_LC3S, self.Q_LCMAIN, self.Q_TC1S,
                       self.Q_TC2S, self.Q_TC3S, self.Q_FEED, self.Q_INJE, self.Q_COMB]

        for queue in self.queues:
            queue.append((0, 0))

        # A dictionary to match mtypes to queues (see _process_recv_message)
        self.queue_dict = {
            ServerInfo.LC1S: self.Q_LC1S,
            ServerInfo.LC2S: self.Q_LC2S,
            ServerInfo.LC3S: self.Q_LC3S,
            ServerInfo.LC_MAINS: self.Q_LCMAIN,
            ServerInfo.TC1S: self.Q_TC1S,
            ServerInfo.TC2S: self.Q_TC2S,
            ServerInfo.TC3S: self.Q_TC3S,
            ServerInfo.PT_FEEDS: self.Q_FEED,
            ServerInfo.PT_COMBS: self.Q_COMB,
            ServerInfo.PT_INJES: self.Q_INJE
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
            else:  # Check mtype to determine what to do
                if mtype == ServerInfo.ACK_VALUE:
                    pass
                elif mtype in ServerInfo.filenames.keys():
                    self.nw.server_info.read_payload(message, nbytes, self.queue_dict[mtype], mtype)
                elif mtype == ServerInfo.TEXT:
                    print(message.decode('utf-8'))
                    # sys.stdout.write(message.decode('utf-8'))
                else:
                    self.logger.error("Received incorrect message header type" + str(mtype))


class GUIFrontend:
    def __init__(self, backend):
        self.backend = backend
        self.root = tk.Tk()
        self.root.resizable(False, False)
        self.root.wm_title("Rice Eclipse Mk-1.1 GUI")

        Pmw.initialise(self.root)

        # Create a notebook and the tabs
        self.notebook = ttk.Notebook(self.root)
        mission_control = ttk.Frame(self.notebook)
        logging = ttk.Frame(self.notebook)
        calibration = ttk.Frame(self.notebook)

        self.notebook.add(mission_control, text='Mission Control')
        self.notebook.add(logging, text='Logging')
        self.notebook.add(calibration, text='Calibration')
        self.notebook.grid(row=1, column=1, sticky='NW')

        # Potential to add styles
        s = ttk.Style()

        s.theme_create("BlueTabs", parent="default", settings={
            "TNotebook": {
                "configure": {"background": "#f0f8ff"}}})

        s.theme_use("default")

        # This figure contains everything to do with matplotlib on the left hand side
        figure, axes_list = plt.subplots(nrows=2, ncols=2)
        self.axes_list = list(axes_list[0]) + list(axes_list[1])
        figure.subplots_adjust(top=.9, bottom=.1, left=.12, right=.95, wspace=.3, hspace=.5)
        figure.set_size_inches(8, 6)
        figure.set_dpi(100)

        # Create a canvas to show this figure under the default tab
        default_canvas = FigureCanvasTkAgg(figure, master=mission_control)
        default_canvas.get_tk_widget().grid(row=1, column=1, sticky="NW")

        self.plots = [axes_list[0][0].plot([0], [0])[0],
                      axes_list[0][1].plot([0], [0])[0],
                      axes_list[1][0].plot([0], [0])[0],
                      axes_list[1][1].plot([0], [0])[0]]

        # plt.setp(self.plots[0], aa=True)

        self.plot_selections = ["LC_MAIN", "LC1S", "TC2S", "PT_INJE"]

        self.animation = animation.FuncAnimation(figure, self.animate, interval=10)

        # This frame contains everything to do with buttons and entry boxes on the right hand side
        control_panel = tk.Frame(background="AliceBlue", width=350, height=625)
        control_panel.grid(row=1, column=2, sticky="NE")

        network_frame = tk.LabelFrame(control_panel, text="Network", background="AliceBlue")

        tk.ttk.Label(network_frame, text="IP", background="AliceBlue").grid(row=1, column=1, sticky="w", padx=15)
        tk.ttk.Label(network_frame, text="port", background="AliceBlue").grid(row=1, column=2, sticky="w", padx=15)

        ip_entry = tk.ttk.Entry(network_frame, width=15)
        ip_entry.insert(tk.END, '192.168.1.137')
        ip_entry.grid(row=2, column=1, padx=15)

        port_entry = tk.ttk.Entry(network_frame, width=5)
        port_entry.insert(tk.END, '1234')
        port_entry.grid(row=2, column=2, padx=15, sticky="w")

        tk.ttk.Button(network_frame, text="Connect", command=lambda: backend.connect(ip_entry.get(), port_entry.get()))\
            .grid(row=3, column=1, pady=(15, 10), padx=15, sticky="w")
        tk.ttk.Button(network_frame, text="Disconnect", command=lambda: backend.nw.disconnect()) \
            .grid(row=3, column=2, pady=(15, 10), padx=15)

        network_frame.grid(row=1, column=1, pady=(7 , 20))

        # Frame for selection of graphs
        graph_frame = tk.LabelFrame(control_panel, text="Graphs", background="AliceBlue")

        self.choices = ["LC1S", "LC2S", "LC3S", "LC_MAIN", "PT_FEED", "PT_INJE", "PT_COMB", "TC1S", "TC2S", "TC3S"]
        self.graph_variables = [tk.StringVar(graph_frame), tk.StringVar(graph_frame),
                                tk.StringVar(graph_frame), tk.StringVar(graph_frame)]
        self.fine_control = tk.BooleanVar(graph_frame)
        option_menus = []

        for i in range(4):
            option_menus.append(
                tk.ttk.OptionMenu(graph_frame, self.graph_variables[i], self.plot_selections[i], *self.choices))
            option_menus[i].config(width=10)
            option_menus[i].grid(row=2 + 2 * int(i > 1), column=i % 2 + 1, padx=10, pady=(0, 10))

        tk.Label(graph_frame, text="Top Left", background="AliceBlue").grid(row=1, column=1, sticky="w", padx=10)
        tk.Label(graph_frame, text="Top Right", background="AliceBlue").grid(row=1, column=2, sticky="w", padx=10)
        tk.Label(graph_frame, text="Bot Left", background="AliceBlue").grid(row=3, column=1, sticky="w", padx=10)
        tk.Label(graph_frame, text="Bot Right", background="AliceBlue").grid(row=3, column=2, sticky="w", padx=10)

        tk.ttk.Checkbutton(graph_frame, text="Show All Data", variable=self.fine_control)\
            .grid(row=5, column=1, sticky="w", padx=15, pady=(5, 15))

        graph_frame.grid(row=2, column=1, pady=15)

        # Frame for controlling the valves
        valve_frame = tk.LabelFrame(control_panel, text="Valve", background="AliceBlue")

        tk.ttk.Button(valve_frame, text="Set Valve", command=lambda: backend.send(ServerInfo.SET_VALVE))\
            .grid(row=1, column=1, padx=15, pady=10)

        tk.ttk.Button(valve_frame, text="Unset Valve", command=lambda: backend.send(ServerInfo.UNSET_VALVE))\
            .grid(row=1, column=2, padx=15, pady=10)

        valve_frame.grid(row=3, column=1, pady=15)

        # Frame for ignition
        ignition_frame = tk.LabelFrame(control_panel, text="Ignition", background="AliceBlue")

        tk.ttk.Label(ignition_frame, text="Burn Time", background="AliceBlue")\
            .grid(row=1, column=1, sticky="w", padx=15)
        tk.ttk.Label(ignition_frame, text="Delay", background="AliceBlue").grid(row=1, column=2, sticky="w", padx=15)

        burn_entry = tk.ttk.Entry(ignition_frame, width=6)
        burn_entry.insert(tk.END, '3')
        burn_entry.grid(row=2, column=1, padx=15, sticky="w")

        delay_entry = tk.ttk.Entry(ignition_frame, width=6)
        delay_entry.insert(tk.END, '0.5')
        delay_entry.grid(row=2, column=2, padx=15, sticky="w")

        # TODO send the ignition length to the backend when we press the button
        set_ignition_button = tk.ttk.Button(ignition_frame, text="IGNITE",
                                            command=lambda: backend.send(ServerInfo.SET_IGNITION))
        set_ignition_image = PhotoImage(file="ignite.gif")
        set_ignition_button.config(image=set_ignition_image)
        set_ignition_button.image = set_ignition_image
        set_ignition_button.grid(row=3, column=1, padx=15, pady=10)

        unset_ignition_button = tk.ttk.Button(ignition_frame, text="UNIGNITE",
                                          command=lambda: backend.send(ServerInfo.UNSET_IGNITION))
        unset_ignition_image = PhotoImage(file="unignite.gif")
        unset_ignition_button.config(image=unset_ignition_image)
        unset_ignition_button.image = unset_ignition_image
        unset_ignition_button.grid(row=3, column=2, padx=15, pady=10)

        ignition_frame.grid(row=4, column=1, pady=(20, 10))

        self.st = Pmw.ScrolledText(logging,
                                   columnheader=1,
                                   usehullsize=1,
                                   hull_width=800,
                                   hull_height=500,
                                   text_wrap='none',
                                   Header_foreground='blue',
                                   Header_padx=4,
                                   hscrollmode="none",
                                   vscrollmode="none",
                                   )

        # Create the column headers
        headerLine = ''
        for column in range(len(self.choices)):
            headerLine = headerLine + ('%-7s   ' % (self.choices[column],))
        headerLine = headerLine[:-3]
        self.st.component('columnheader').insert('0.0', headerLine)

        self.st.tag_configure('yellow', background='yellow')

        self.st.grid(row=1, column=1)

    def animate(self, *fargs):
        # Randomly generate some data to plot
        for queue in self.backend.queues:
            length = len(queue) - 1
            for j in range(1, 11):
                queue.append((random.randint(0, 1000), queue[length][1] + j))
                # queue.append((queue[length][1] + j, queue[length][1] + j))
            # print (queue)
        # print (self.backend.queues[0][-10:])

        # Only graph if we are on the mission control tab
        if self.notebook.index(self.notebook.select()) == 0:
            self.update_graphs()
        elif self.notebook.index(self.notebook.select()) == 1:
           self.update_log_displays()

    def update_graphs(self):
        for i in range(4):
            # Get which graph the user has selected and get the appropriate queue from the backend
            graph_selection = self.graph_variables[i].get()
            data_queue = self.backend.queue_dict[str_to_byte[graph_selection]]
            data_length = data_lengths[graph_selection]

            if self.fine_control.get():
                data_ratio = 1
            else:
                data_ratio = int(data_lengths[graph_selection] / samples_to_keep[graph_selection])
            # print (data_ratio)

            self.plots[i].set_xdata([t for cal, t in data_queue[-data_length::data_ratio]])
            self.plots[i].set_ydata([cal for cal, t in data_queue[-data_length::data_ratio]])

            self.axes_list[i].relim()

            # Rescaling the axes is apparently very expensive, so only do it if the data is out of bounds
            all_y_data = [cal for cal, t in data_queue[-data_length:]]
            if min(all_y_data) < self.axes_list[i].get_ylim()[0] or \
                    max(all_y_data) > self.axes_list[i].get_ylim()[1]:
                self.axes_list[i].autoscale_view(scalex=True, scaley=True)
            else:
                self.axes_list[i].autoscale_view(scalex=True, scaley=False)

            # We have to do this even if we don't change graphs because the labels get erased after we scale the axes
            self.axes_list[i].set_title(graph_selection)
            self.axes_list[i].set_xlabel(labels[graph_selection][0])
            self.axes_list[i].set_ylabel(labels[graph_selection][1])

            self.plot_selections[i] = graph_selection

    def update_log_displays(self):
        self.st.clear()
        # Create the data rows and the row headers
        numRows = 20
        tagList = []
        for row in range(1, numRows):
            dataLine = ''
            x = row / 5.0
            for column in range(len(self.choices)):
                data_queue = self.backend.queue_dict[str_to_byte[self.choices[column]]]
                value = data_queue[max(-len(data_queue) + 1, -numRows + row)][0]
                # print ("value", value)
                data = str(value)[:9]
                if value < 500:
                    tag1 = '%d.%d' % (row, len(dataLine))
                    tag2 = '%d.%d' % (row, len(dataLine) + len(data))
                    tagList.append(tag1)
                    tagList.append(tag2)
                data = '%-7s' % (data,)
                dataLine = dataLine + data + '   '

            dataLine = dataLine + '\n'
            self.st.insert('end', dataLine)
            # print ("data", dataLine)
            # print ("tags", tuple(tagList))

        averages = ''
        for column in range(len(self.choices)):
            data_queue = self.backend.queue_dict[str_to_byte[self.choices[column]]]
            average = sum([cal for cal, t in data_queue[-10:]]) / 10.0
            data = str(average)[:9]
            data = '%-7s' % (data,)
            averages = averages + data + '   '
        self.st.insert('end', averages)

        self.st.tag_add(("yellow"), '20.0', '20.' + str(len(averages) - 4))
        # print ('20.' + str(len(averages)))



frontend = GUIFrontend(GUIBackend([], [], [], [], [], [], [], [], [], []))
frontend.root.mainloop()
