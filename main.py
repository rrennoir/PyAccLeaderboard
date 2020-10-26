import socket
import tkinter as tk
import threading
import queue
from tkinter import StringVar
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


class Table(tk.Frame):

    def __init__(self, root, header, row: int) -> None:
        tk.Frame.__init__(self, root)
        self.row = row
        self.column = len(header)
        self.labels = []

        for i in range(self.row):
            column_labels = []
            for j in range(self.column):

                if i == 0:
                    label = tk.Label(root, text=header[j]["text"], bg="green")
                    label.grid(row=i, column=j)
                    column_labels.append(label)

                else:
                    label = tk.Label(root, text="", bg="yellow")
                    label.grid(row=i, column=j)
                    column_labels.append(label)

            self.labels.append(column_labels)

    def update_text(self, data):

        entries = data.entry_list.entry_list
        nb_entries = len(entries)

        ordered_entries = {}
        for entry in entries:

            car_id = entry.car_index
            car_data = data.leaderboard_data[car_id]
            if "position" not in car_data.keys():
                return

            position = car_data["position"]

            ordered_entries.update({position: car_data})

        for i in range(1, nb_entries):
            for j in range(self.column):

                if j == 0:
                    string = str(ordered_entries[i]["position"])

                elif j == 1:
                    string = ordered_entries[i]["car number"]

                elif j == 2:
                    string = ordered_entries[i]["cup category"]

                elif j == 3:
                    string = ordered_entries[i]["manufacturer"]

                elif j == 4:
                    string = str(ordered_entries[i]["team"])

                elif j == 5:
                    string = from_ms(ordered_entries[i]["best session lap"])

                elif j == 6:
                    string = from_ms(ordered_entries[i]["current lap"])

                elif j == 7:
                    string = ordered_entries[i]["lap"]

                elif j == 8:
                    string = from_ms(ordered_entries[i]["last lap"])

                elif j == 9 and len(ordered_entries[i]["sectors"]) > 0:
                    string = from_ms(ordered_entries[i]["sectors"][0])

                elif j == 10 and len(ordered_entries[i]["sectors"]) > 0:
                    string = from_ms(ordered_entries[i]["sectors"][1])

                elif j == 11 and len(ordered_entries[i]["sectors"]) > 0:
                    string = from_ms(ordered_entries[i]["sectors"][2])

                elif j == 12:
                    string = "0"

                elif j == 13:
                    string = ordered_entries[i]["car location"]

                else:
                    string = ""

                self.labels[i][j].configure(text=string)


class LeaderboardGui:

    def __init__(self, queue_in, header) -> None:

        self.queue_in = queue_in
        self.gui_root = tk.Tk()
        self.gui_root.configure(background="black")
        self.status = StringVar(self.gui_root)

        self.table = Table(self.gui_root, header, 26)
        self.delay = 1000

        self.gui_root.after(self.delay, self.read_queue)

    def read_queue(self) -> None:

        print("read queue")

        try:
            data = self.queue_in.get()
            self.table.update_text(data)
            self.queue_in.put(data)

        except queue.Empty:
            print("read_queue: queue empty")

        self.gui_root.after(self.delay, self.read_queue)


def acc_run(q):

    global stop_worker

    print("enter acc run thread")
    instance = q.get()

    while not stop_worker:
        instance.update()
        q.put(instance)


stop_worker = False

if __name__ == "__main__":

    table_header = [
        {
            "text": "Postion",
            "width": 10
        },
        {
            "text": "Car",
            "width": 0
        },
        {
            "text": "Class",
            "width": 0
        },
        {
            "text": "Brand",
            "width": 0
        },
        {
            "text": "Team and Driver",
            "width": 0
        },
        {
            "text": "Best Lap",
            "width": 0
        },
        {
            "text": "Current Lap",
            "width": 0
        },
        {
            "text": "Lap",
            "width": 4
        },
        {
            "text": "Lap Time and Gap",
            "width": 13
        },
        {
            "text": "S1",
            "width": 3
        },
        {
            "text": "S2",
            "width": 3
        },
        {
            "text": "S3",
            "width": 3
        },
        {
            "text": "Pit Stops",
            "width": 6
        },
        {
            "text": "Location",
            "width": 0
        }]

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", 3400))

    test_instance = accProtocol.Leaderboard(sock, "127.0.0.1", 9000)

    test_instance.connect("Ryan Rennoir", "asd", 250, "")

    q = queue.Queue()

    gui = LeaderboardGui(q, table_header)

    q.put(test_instance)

    thread_acc = threading.Thread(target=acc_run, args=(q, ))
    thread_acc.start()

    gui.gui_root.mainloop()

    stop_worker = True

    thread_acc.join()
    print("ACC Worker Thread closed")
    test_instance.disconnect()
    sock.close()
    print("Socket closed")
