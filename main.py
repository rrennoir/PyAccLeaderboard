import copy
import datetime
import queue
import socket
import threading
import tkinter as tk
from tkinter import StringVar
import sys

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
                if len(data[entry]) > 0 and position == data[entry]["position"]:
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


class LeaderboardGui:

    def __init__(self, queue_in, header) -> None:

        self.queue_in = queue_in
        self.gui_root = tk.Tk()
        self.gui_root.configure(background="black")
        self.status = StringVar(self.gui_root)

        self.table = Table(self.gui_root, header, 26)
        self.data = None
        self.delay = 1000

        self.gui_root.after(self.delay, self.read_queue)

    def read_queue(self) -> None:

        print("read queue")

        try:
            self.data = self.queue_in.get_nowait()
            self.table.update_text(self.data)

        except queue.Empty:
            print("read_queue: queue empty")

        self.gui_root.after(self.delay, self.read_queue)


def acc_run(instance, q):

    global stop_worker

    print("enter acc run thread")
    last_message = datetime.datetime.now()

    while not stop_worker:

        instance.update()

        now = datetime.datetime.now()
        if (now - last_message).total_seconds() > 1:
            print("add to queue")
            data_copy = copy.deepcopy(instance.leaderboard_data)
            last_message = now
            q.put(data_copy)


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

    test_instance = accProtocol.Leaderboard(sock, ip, 9000)

    test_instance.connect("Ryan Rennoir", "asd", 250, "")

    q = queue.Queue()

    thread_acc = threading.Thread(target=acc_run, args=(test_instance, q))
    thread_acc.start()

    gui = LeaderboardGui(q, table_header)

    gui.gui_root.mainloop()

    stop_worker = True

    thread_acc.join()
    print("ACC Worker Thread closed")
    test_instance.disconnect()
    sock.close()
    print("Socket closed")
