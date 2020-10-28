import copy
import datetime
import queue
import socket
import sys
import threading
import tkinter as tk

import accProtocol


def from_ms(time: int) -> str:

    minute = time // 60_000
    second = time // 1000 - minute * 60
    millisecond = time - minute * 60_000 - second * 1000

    if second < 10:
        second = "0" + str(second)

    else:
        second = str(second)

    if millisecond < 10:
        millisecond = "00" + str(millisecond)

    elif millisecond < 100:
        millisecond = "0" + str(millisecond)

    else:
        millisecond = str(millisecond)

    return f"{minute}:{second}.{millisecond}"


def create_cell(parent, text, bg, max_width=0, height=1):

    width = len(text)
    if max_width > 0:
        width = max_width

    cell = tk.Label(
        parent, text=text, bg=bg, width=width, height=height, justify=tk.LEFT)

    return cell


class Table(tk.Frame):

    def __init__(self, root, header, row: int) -> None:
        tk.Frame.__init__(self, root)
        self.row = row
        self.column = len(header)
        self.labels = []

        for i in range(self.row):
            column_labels = []
            for j in range(self.column):

                width = header[j]["width"]
                if i == 0:
                    text = header[j]["text"]
                    label = create_cell(root, text, "#f0f0f0", width, 2)

                    label.grid(row=i, column=j)
                    column_labels.append(label)

                else:
                    if i % 2 == 0:
                        background = "#e0e0e0"

                    else:
                        background = "#878787"

                    label = create_cell(root, "", background, width, 2)

                    if j == 4:
                        label.grid(row=i, column=j, sticky=tk.W)
                    else:
                        label.grid(row=i, column=j)

                    column_labels.append(label)

            self.labels.append(column_labels)

    def update_text(self, data):

        entries = []
        position = 1
        nb_entries = len(data)
        while position <= nb_entries:

            for entry in data.keys():
                if (len(data[entry]) > 0 and
                        position == data[entry]["position"]):
                    entries.append(data[entry])

            position += 1

        if nb_entries == 0 or len(entries) == 0:
            return

        entry_id = 0
        for grid_y in range(1, nb_entries + 1):

            for grid_x in range(self.column):

                if grid_x == 0:
                    string = entries[entry_id]["position"]

                elif grid_x == 1:
                    string = entries[entry_id]["car number"]

                elif grid_x == 2:
                    string = entries[entry_id]["cup category"]

                elif grid_x == 3:
                    string = entries[entry_id]["manufacturer"]

                elif grid_x == 4:
                    team = entries[entry_id]["team"]
                    first_name = entries[entry_id]["driver"]['first name']
                    last_name = entries[entry_id]["driver"]['last name']
                    string = f"{team}\n{first_name} {last_name}"

                elif grid_x == 5:
                    string = from_ms(entries[entry_id]["best session lap"])

                elif grid_x == 6:
                    string = from_ms(entries[entry_id]["current lap"])

                elif grid_x == 7:
                    string = entries[entry_id]["lap"]

                elif grid_x == 8:
                    string = from_ms(entries[entry_id]["last lap"])

                elif grid_x == 9 and len(entries[entry_id]["sectors"]) > 0:
                    string = from_ms(entries[entry_id]["sectors"][0])

                elif grid_x == 10 and len(entries[entry_id]["sectors"]) > 0:
                    string = from_ms(entries[entry_id]["sectors"][1])

                elif grid_x == 11 and len(entries[entry_id]["sectors"]) > 0:
                    string = from_ms(entries[entry_id]["sectors"][2])

                elif grid_x == 12:
                    string = "0"

                elif grid_x == 13:
                    string = entries[entry_id]["car location"]

                else:
                    string = ""

                self.labels[grid_y][grid_x].configure(text=string)

            entry_id += 1

    def clear_entries(self) -> None:

        for grid_y in range(1, self.row):
            for grid_x in range(self.column):

                self.labels[grid_y][grid_x].configure(text="")


class LeaderboardGui:

    def __init__(self, queue_in, header) -> None:

        self.queue_in = queue_in
        self.gui_root = tk.Tk()
        self.gui_root.title("PyAccLeaderboard")
        self.gui_root.configure(background="black")
        self.status = tk.StringVar(self.gui_root)

        self.table = Table(self.gui_root, header, 26)
        self.data = None
        self.local_car_ids = []
        self.delay = 1000

        self.gui_root.after(self.delay, self.read_queue)

    def read_queue(self) -> None:

        try:
            new_data = self.queue_in.get_nowait()

            valide_data = True
            for entry in new_data:
                if len(new_data[entry]) == 0:
                    valide_data = False

            if valide_data:
                self.data = new_data
                self.update_local_entries()
                self.table.update_text(self.data)

        except queue.Empty:
            print("Read Queue: queue empty")

        self.gui_root.after(self.delay, self.read_queue)

    def update_local_entries(self) -> None:

        new_entries = False
        if len(self.data) != len(self.local_car_ids):
            new_entries = True

        else:
            for key in self.data.keys():
                if self.data[key]["car id"] not in self.local_car_ids:
                    new_entries = True

        if new_entries:
            print("Reviced new entry list")
            self.local_car_ids.clear()
            for key in self.data:
                self.local_car_ids.append(self.data[key]["car id"])

            print("Clearing leaderboard cell...")
            self.table.clear_entries()


def acc_run(info: dict, q: queue.Queue):

    print("Starting ACC Worker Thread...")
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
            if (now - last_message).total_seconds() > 1:
                data_copy = copy.deepcopy(instance.leaderboard_data)
                last_message = now
                q.put(data_copy)

    print("Closing ACC Worker Thread...")
    instance.disconnect()


stop_worker = False

if __name__ == "__main__":

    table_header = [
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
            "text": "Best Lap",
            "width": 8
        },
        {
            "text": "Current Lap",
            "width": 8
        },
        {
            "text": "Lap",
            "width": 3
        },
        {
            "text": "Lap Time\nGap",
            "width": 7
        },
        {
            "text": "S1",
            "width": 7
        },
        {
            "text": "S2",
            "width": 7
        },
        {
            "text": "S3",
            "width": 7
        },
        {
            "text": "Pit Stops",
            "width": 9
        },
        {
            "text": "Location",
            "width": 8
        }]

    args = sys.argv
    argc = len(args)

    ip = "127.0.0.1"
    port = 9000

    if argc > 1:
        ip = args[1]

    if argc > 2:
        port = int(args[2])

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

    gui = LeaderboardGui(q, table_header)

    gui.gui_root.mainloop()

    stop_worker = True

    thread_acc.join()
    sock.close()
    print("Socket closed")
