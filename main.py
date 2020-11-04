import copy
import datetime
from PIL import Image, ImageTk
import queue
import logging
import socket
import sys
import time
import threading
import tkinter as tk
from tkinter.font import Font

import accProtocol

brands = {
    0: {
        "Brand": "Porsche",
        "Model": "Porsche 991 GT3 R (2018)"
    },
    1: {
        "Brand": "AMG",
        "Model": "Mercedes-AMG GT3 (2015)"
    },
    2: {
        "Brand": "Ferrari",
        "Model": "Ferrari 488 GT3 (2018)"
    },
    3: {
        "Brand": "Audi",
        "Model": "Audi R8 LMS GT3 (2015)"
    },
    4: {
        "Brand": "Lamborghini",
        "Model": "Lamborghini Huracan GT3 (2015)"
    },
    5: {
        "Brand": "McLaren",
        "Model": "McLaren 650s GT3 (2015)"
    },
    6: {
        "Brand": "Nissan",
        "Model": "Nissan GT-R Nismo GT3 (2018)"
    },
    7: {
        "Brand": "BMW",
        "Model": "BMW M6 GT3 (2017)"
    },
    8: {
        "Brand": "Bentley",
        "Model": "Bentley Continental GT3 (2019)"
    },
    9: {
        "Brand": "Porsche",
        "Model": "Porsche 991.2 GT3 Cup (2017)"
    },
    10: {
        "Brand": "Nissan",
        "Model": "Nissan GT-R Nismo GT3 (2015)"
    },
    11: {
        "Brand": "Bentley",
        "Model": "Bentley Continental GT3 (2015)"
    },
    12: {
        "Brand": "Aston",
        "Model": "Aston Martin Vantage V12 GT3 (2013)"
    },
    13: {
        "Brand": "Reiter",
        "Model": "Lamborghini Gallardo R-EX GT3 (2017)"
    },
    14: {
        "Brand": "Jaguar",
        "Model": "Jaguar G3 GT3 (2012)"
    },
    15: {
        "Brand": "Lexus",
        "Model": "Lexus RF C GT3 (2017)"
    },
    16: {
        "Brand": "Lamborghini",
        "Model": "Lamborghini Huracan Evo GT3 (2019)"
    },
    17: {
        "Brand": "Honda",
        "Model": "Honda NSX GT3 (2017)"
    },
    18: {
        "Brand": "Lamborghini",
        "Model": "Lamborghini Huracan SuperTrofeo (2015)"
    },
    19: {
        "Brand": "Audi",
        "Model": "Audi R8 LMS Evo GT3 (2019)"
    },
    20: {
        "Brand": "Honda",
        "Model": "Honda NSX GT3 (2019)"
    },
    21: {
        "Brand": "Honda",
        "Model": "Honda NSX GT3 (2019)"
    },
    22: {
        "Brand": "McLaren",
        "Model": "McLaren 720s GT3 (2019)"
    },
    23: {
        "Brand": "Porsche",
        "Model": "Porsche 991II GT3 R (2019)"
    },
    50: {
        "Brand": "Alpine",
        "Model": "Alpine A110 GT4 (2018)"
    },
    51: {
        "Brand": "Aston",
        "Model": "Aston Martin Vantage V8 GT4 (2018)"
    },
    52: {
        "Brand": "Audi",
        "Model": "Audi R8 LMS GT4 (2018)"
    },
    53: {
        "Brand": "BMW",
        "Model": "BMW M4 GT4 (2018)"
    },
    55: {
        "Brand": "Chevrolet",
        "Model": "Chevrolet Camaro GT4 (2017)"
    },
    56: {
        "Brand": "Ginetta",
        "Model": "Ginetta G55 GT4 (2012)"
    },
    57: {
        "Brand": "KTM",
        "Model": "KTM X-Bow GT (2016)"
    },
    58: {
        "Brand": "Maserati",
        "Model": "Maserati MC GT4 (2016)"
    },
    59: {
        "Brand": "McLaren",
        "Model": "McLaren 570s GT4 (2016)"
    },
    60: {
        "Brand": "AMG",
        "Model": "Mercedes-AMG GT4 (2016)"
    },
    61: {
        "Brand": "Porsche",
        "Model": "Porsche 718 Cayman GT4 (2019)"
    },
}


def load_images() -> dict:

    image_cache = {}
    for car_model in brands.keys():

        name = brands[car_model]["Brand"]

        if name not in image_cache:
            file = Image.open(f"images/logos/{name}.png")
            image = ImageTk.PhotoImage(file)
            image_cache[name] = image
            file.close()

        brands[car_model]["Logo"] = image_cache[name]


def from_ms(time: int) -> str:
    """
    Convert millisconds into a string in format mm:ss.ms
    """

    minute = time // 60_000
    second = time // 1000 - minute * 60
    millisecond = time - minute * 60_000 - second * 1000

    if second < 10:
        second = "0" + str(second)

    else:
        second = str(second)

    if millisecond < 10:
        millisecond = f"00{millisecond}"

    elif millisecond < 100:
        millisecond = f"0{millisecond}"

    else:
        millisecond = str(millisecond)

    return f"{minute}:{second}.{millisecond}"


def from_date_time(time: datetime.datetime) -> str:
    """
    Return a string in format hh:mm:ss
    """

    days = time.day - 1
    hours = time.hour
    minutes = time.minute
    seconds = time.second

    hours = days * 24 + hours - 1

    if hours < 10:
        hours = f"0{hours}"

    if minutes < 10:
        minutes = f"0{minutes}"

    if seconds < 10:
        seconds = f"0{seconds}"

    return f"{hours}:{minutes}:{seconds}"


def create_cell(parent, text, bg="white", font=None, max_width=0,
                height=1, anchor=tk.CENTER, relief=tk.FLAT):

    width = len(text)
    if max_width > 0:
        width = max_width

    if font:
        cell = tk.Label(
            parent, text=text, bg=bg, width=width, height=height,
            justify=tk.LEFT, anchor=anchor, font=font, relief=relief)

    else:
        cell = tk.Label(
            parent, text=text, bg=bg, width=width, height=height,
            justify=tk.LEFT, anchor=anchor, relief=relief)

    return cell


class Table(tk.Frame):

    def __init__(self, parent, font, header, color_1, color_2, row=1) -> None:
        tk.Frame.__init__(self, parent)
        self.row = row
        self.column = len(header)
        self.labels = []
        self.color_1 = color_1
        self.color_2 = color_2
        load_images()

        for i in range(self.row):
            column_labels = []
            for j in range(self.column):

                width = header[j]["width"]
                if i % 2 == 0:
                    background = self.color_1

                else:
                    background = self.color_2

                if j == 4:
                    label = create_cell(
                        parent, "", background, font, width, 2, tk.W)
                else:
                    label = create_cell(parent, "", background, font, width, 2)

                label.grid(row=i, column=j, padx=1, sticky=tk.NSEW)

                column_labels.append(label)

            self.labels.append(column_labels)

    def update_text(self, data, local_data):

        entries = []
        position = 1
        data_entries = data["entries"]
        nb_entries = len(data_entries)
        while position <= nb_entries:

            for entry in data_entries.keys():
                if (len(data_entries[entry]) > 0 and
                        position == data_entries[entry]["position"]):
                    entries.append(data_entries[entry])

            position += 1

        if nb_entries == 0 or len(entries) == 0:
            return

        for grid_y in range(nb_entries):

            for grid_x in range(self.column):

                color_changed = False
                color = None

                if grid_x == 0:
                    string = entries[grid_y]["position"]

                elif grid_x == 1:
                    string = entries[grid_y]["car_number"]

                elif grid_x == 2:
                    string = entries[grid_y]["cup_category"]

                elif grid_x == 3:

                    model_number = entries[grid_y]["manufacturer"]
                    logo = brands[model_number]["Logo"]

                    if grid_y % 2 == 0:
                        color = self.color_1

                    else:
                        color = self.color_2

                    label = tk.Label(self.master, bg=color, image=logo)
                    label.image = logo
                    label.place(x=0, y=0)
                    label.grid(row=grid_y, column=grid_x,
                               padx=1, sticky=tk.NSEW)

                    self.labels[grid_y][grid_x] = label
                    string = ""

                elif grid_x == 4:
                    team = entries[grid_y]["team"]
                    first_name = entries[grid_y]["driver"]['first_name']
                    last_name = entries[grid_y]["driver"]['last_name']
                    string = f"{team}\n{first_name} {last_name}"

                elif grid_x == 5:
                    string = from_ms(entries[grid_y]["best_session_lap"])

                elif grid_x == 6:
                    string = from_ms(entries[grid_y]["current_lap"])

                elif grid_x == 7:
                    string = entries[grid_y]["lap"]

                elif grid_x == 8:
                    string = from_ms(entries[grid_y]["last_lap"])

                elif grid_x == 9 and len(entries[grid_y]["sectors"]) > 0:
                    string = from_ms(entries[grid_y]["sectors"][0])

                elif grid_x == 10 and len(entries[grid_y]["sectors"]) > 0:
                    string = from_ms(entries[grid_y]["sectors"][1])

                elif grid_x == 11 and len(entries[grid_y]["sectors"]) > 0:
                    string = from_ms(entries[grid_y]["sectors"][2])

                elif grid_x == 12:
                    car_id = entries[grid_y]["car_id"]
                    pits = local_data[car_id]["pits"]
                    string = f"{pits}"

                elif grid_x == 13:

                    location = entries[grid_y]["car_location"]
                    color_changed = True
                    if location == "Track":
                        string = ""

                        if grid_y % 2 == 0:
                            color = self.color_1

                        else:
                            color = self.color_2

                    else:
                        # Gas station emoji
                        string = "\u26FD"

                        if location == "Pitlane":
                            color = "red"

                        elif location == "PitEntry":
                            color = "blue"

                        elif location == "PitExit":
                            color = "green"

                else:
                    string = ""

                if color_changed:
                    self.labels[grid_y][grid_x].configure(
                        text=string, bg=color)

                else:
                    self.labels[grid_y][grid_x].configure(text=string)

    def clear_entries(self) -> None:
        """
        Clear all entries in the table
        """

        for grid_y in range(self.row):
            for grid_x in range(self.column):

                self.labels[grid_y][grid_x].configure(text="")


class LeaderboardGui(tk.Tk):

    def __init__(self, queue_in=None, info=None, *args, **kargs) -> None:
        tk.Tk.__init__(self, *args, **kargs)

        self.title("PyAccLeaderboard")
        self.configure(background="black")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.font = Font(family="calibri", size=11)
        self.info_font = Font(family="calibri", size=12)

        # Base Frame
        main_frame = tk.Frame(self, bg="black")
        main_frame.grid(sticky=tk.NSEW)
        main_frame.columnconfigure(0, weight=1)

        # App Frame for leaderboard and orther info
        app_frame = tk.Frame(main_frame, bd=2, relief=tk.SUNKEN)
        app_frame.grid(row=0, column=0, sticky=tk.NSEW)

        # Session Information
        info_frame = tk.Frame(app_frame)
        info_frame.grid(row=0, column=0, sticky=tk.NSEW, pady=(0, 2))
        self.session_info = []
        self.build_session_info(info_frame, info["info"])

        # Create a Frame with the header
        header_frame = tk.Frame(app_frame)
        header_frame.grid(row=1, column=0, sticky=tk.NW)
        self.build_header(header_frame, info["table"])

        frame_canvas = tk.Frame(app_frame)
        frame_canvas.grid(row=2, column=0, pady=(5, 0), sticky=tk.NW)

        canvas = tk.Canvas(frame_canvas)
        canvas.grid(row=0, column=0, sticky=tk.NW)

        # Create vertical scrollbar to move the table
        v_scrollbar = tk.Scrollbar(
            main_frame, orient=tk.VERTICAL, command=canvas.yview)
        v_scrollbar.grid(row=0, column=1, sticky=tk.NS)
        canvas.configure(yscrollcommand=v_scrollbar.set)

        table_frame = tk.Frame(canvas)
        self.table = Table(
            table_frame, self.font, info["table"], "#c0c0c0", "#a0a0a0", 82)

        canvas.create_window((0, 0), window=table_frame, anchor=tk.NW)

        table_frame.update_idletasks()
        bbox = canvas.bbox(tk.ALL)

        w, h = bbox[2] - bbox[1], bbox[3] - bbox[1]
        dw, dh = int((w / 14) * 14), int((h / 82) * 10)
        canvas.configure(scrollregion=bbox, width=dw, height=dh)

        self.queue_in = queue_in
        self.data = None
        self.local_data = {
            "session": "",
            "entries": {}
        }
        self.local_car_ids = []
        self.delay = 500

        self.after(self.delay, self.read_queue)

    def read_queue(self) -> None:

        logging.debug("Read Queue: reading queue")
        try:
            new_data = self.queue_in.get_nowait()

            valide_data = True
            for entry in new_data["entries"]:
                if len(new_data["entries"][entry]) == 0:
                    valide_data = False

            if valide_data:
                self.data = new_data
                self.update_local_entries()
                self.table.update_text(self.data, self.local_data["entries"])
                self.update_session()

        except queue.Empty:
            logging.debug("Read Queue: queue empty")

        self.after(self.delay, self.read_queue)

    def update_local_entries(self) -> None:

        entries = self.data["entries"]
        local_entries = self.local_data["entries"]
        session = self.data["session"]["session_type"]
        local_session = self.local_data["session"]

        new_entries = False
        if len(entries) != len(local_entries):
            new_entries = True

        else:
            for key in entries.keys():
                if entries[key]["car_id"] not in local_entries:
                    new_entries = True

        if new_entries:
            logging.debug("Reviced new entry list")
            new_data = {}

            for key in entries.keys():

                car_id = entries[key]["car_id"]
                if car_id in local_entries:
                    new_data.update({car_id: local_entries[car_id]})

                else:
                    new_data.update({car_id: {
                        "location": "Pitlane",
                        "pits": 0
                    }})

            self.local_data.update({"entries": new_data})
            logging.debug("Clearing leaderboard cell...")
            self.table.clear_entries()

        elif session != local_session:
            for car_id in local_entries:
                local_entries.update({car_id: {
                    "location": "Pitlane",
                    "pits": 0
                }})

            self.local_data["session"] = session

        else:
            for car_id in local_entries:

                previous = local_entries[car_id]["location"]
                actual = entries[car_id]["car_location"]
                if previous == "Track" and actual != "Track":
                    local_entries[car_id]["pits"] += 1

                local_entries[car_id]["location"] = actual

    def build_session_info(self, parent, info) -> None:

        for i in range(len(info)):
            width = info[i]["width"]
            cell = create_cell(
                parent, "", font=self.info_font,
                max_width=width, relief=tk.RIDGE)

            cell.grid(row=0, column=i, padx=2)
            self.session_info.append(cell)

    def update_session(self) -> None:

        session = self.data["session"]
        if len(session) > 0:
            for i, cell in enumerate(self.session_info):
                if i == 0:
                    cell.configure(text=f"Session: {session['session_type']}")

                elif i == 1:
                    time_left = from_date_time(session["session_end_time"])
                    cell.configure(text=f"Time left: {time_left}")

                elif i == 2:
                    time_elapsed = from_date_time(session['session_time'])
                    cell.configure(text=f"Time elapsed: {time_elapsed}")

                elif i == 3:
                    air_temps = session["air_temp"]
                    cell.configure(text=f"Air: {air_temps}°C")

                elif i == 4:
                    track_temps = session["track_temp"]
                    cell.configure(text=f"Track: {track_temps}°C")

                elif i == 5:
                    clouds = session["clouds"]
                    cell.configure(text=f"Clouds: {clouds}%")

                elif i == 6:
                    rain_level = session["rain_level"]
                    cell.configure(text=f"Rain: {rain_level}%")

                elif i == 7:
                    wetness = session["wetness"]
                    cell.configure(text=f"Wetness: {wetness}%")

    def build_header(self, parent, header) -> None:

        for column, info in enumerate(header):

            text = info["text"]
            color = "#8a8a8a"
            width = info["width"]

            if column == 4:
                # Put Team and Driver name to the far left of the cell
                cell = create_cell(parent, text, color,
                                   self.font, width, 2, tk.W)

            else:
                cell = create_cell(parent, text, color, self.font, width, 2)

            if column == 0:
                cell.grid(row=0, column=column, padx=(3, 1), sticky=tk.NSEW)

            else:
                cell.grid(row=0, column=column, padx=1, sticky=tk.NSEW)


def acc_run(info: dict, q: queue.Queue):

    logging.debug("Starting ACC Worker Thread...")

    global stop_worker

    socket = info["socket"]
    ip = info["ip"]
    port = info["port"]
    name = info["name"]
    password = info["password"]
    speed = info["speed"]
    cmd_password = info["cmd_password"]

    instance = accProtocol.Leaderboard(socket, ip, port)

    instance.connect(name, password, speed, cmd_password)

    last_connection = datetime.datetime.now()
    last_message = datetime.datetime.now()
    while not stop_worker:

        now = datetime.datetime.now()
        # if connection was lost or not established wait 2s before asking again
        if (not instance.connected and
                (now - last_connection).total_seconds() > 2):
            instance.connect(name, password, speed, cmd_password)
            last_connection = datetime.datetime.now()

        else:
            instance.update()

            # Send data to the queue at the same rate
            # as the GUI check the queue
            if (now - last_message).total_seconds() > 0.550:
                data_copy = copy.deepcopy(instance.leaderboard_data)
                last_message = now
                q.put(data_copy)

    logging.debug("Closing ACC Worker Thread...")
    instance.disconnect()


stop_worker = False

if __name__ == "__main__":

    gui_info = {
        "info": [
            {
                "layout": "Session",
                "width": 16
            },
            {
                "layout": "Time left",
                "width": 17
            },
            {
                "layout": "Time elapsed",
                "width": 21
            },
            {
                "layout": "Air Temps",
                "width": 9
            },
            {
                "layout": "Track Temps",
                "width": 11
            },
            {
                "layout": "Clouds",
                "width": 12
            },
            {
                "layout": "Rain",
                "width": 10
            },
            {
                "layout": "Wetness",
                "width": 14
            }
        ],
        "table": [
            {
                "text": "Rank",
                "width": 4
            },
            {
                "text": "Car",
                "width": 3
            },
            {
                "text": "Class",
                "width": 5
            },
            {
                "text": "Brand",
                "width": 5
            },
            {
                "text": "Team\nDriver",
                "width": 30
            },
            {
                "text": "Best",
                "width": 8
            },
            {
                "text": "Current",
                "width": 8
            },
            {
                "text": "Lap",
                "width": 3
            },
            {
                "text": "Last\nGap",
                "width": 8
            },
            {
                "text": "S1",
                "width": 8
            },
            {
                "text": "S2",
                "width": 8
            },
            {
                "text": "S3",
                "width": 8
            },
            {
                "text": "Stops",
                "width": 5
            },
            {
                # Location
                "text": "",
                "width": 3
            }
        ]
    }

    args = sys.argv
    argc = len(args)

    ip = "127.0.0.1"
    port = 9000

    for arg in args:
        if arg.startswith("-ip"):
            ip = args[1][3:]

        if arg.startswith("-p"):
            port = int(arg[2:])

    log_format = "%(asctime)s - %(levelname)s: %(message)s"
    time_format = "%H:%M:%S"
    if "-debug" in args:
        logging.basicConfig(format=log_format,
                            level=logging.DEBUG, datefmt=time_format)

    else:
        logging.basicConfig(format=log_format,
                            level=logging.WARNING, datefmt=time_format)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", 3400))

    instance_info = {
        "ip": ip,
        "port": port,
        "socket": sock,
        "name": "Ryan Rennoir",
        "password": "asd",
        "speed": 250,
        "cmd_password": ""
    }

    q = queue.Queue()

    thread_acc = threading.Thread(target=acc_run, args=(instance_info, q))
    thread_acc.start()

    gui = LeaderboardGui(queue_in=q, info=gui_info)

    gui.mainloop()

    stop_worker = True

    thread_acc.join()
    sock.close()
    logging.debug("Socket closed")
