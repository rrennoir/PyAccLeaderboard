from Cursor import Cursor
from enum import Enum, auto
import datetime
import sys


def write_int(data: int, type: str) -> bytes:

    if type == "u8":
        return (data).to_bytes(1, sys.byteorder, signed=False)

    elif type == "u16":
        return (data).to_bytes(2, sys.byteorder, signed=False)

    elif type == "u32":
        return (data).to_bytes(4, sys.byteorder, signed=False)

    elif type == "i16":
        return (data).to_bytes(2, sys.byteorder, signed=True)

    elif type == "i32":
        return (data).to_bytes(4, sys.byteorder, signed=True)

    else:
        print("Incorrect type")


def write_str(string: str) -> bytes:

    data = b""
    data += write_int(len(string), "u16")
    data += bytearray(string, "utf-8")

    return data


class Nationality(Enum):

    Any = 0
    Italy = 1
    Germany = 2
    France = 3
    Spain = 4
    GreatBritain = 5
    Hungary = 6
    Belgium = 7
    Switzerland = 8
    Austria = 9
    Russia = 10
    Thailand = 11
    Netherlands = 12
    Poland = 13
    Argentina = 14
    Monaco = 15
    Ireland = 16
    Brazil = 17
    SouthAfrica = 18
    PuertoRico = 19
    Slovakia = 20
    Oman = 21
    Greece = 22
    SaudiArabia = 23
    Norway = 24
    Turkey = 25
    SouthKorea = 26
    Lebanon = 27
    Armenia = 28
    Mexico = 29
    Sweden = 30
    Finland = 31
    Denmark = 32
    Croatia = 33
    Canada = 34
    China = 35
    Portugal = 36
    Singapore = 37
    Indonesia = 38
    USA = 39
    NewZealand = 40
    Australia = 41
    SanMarino = 42
    UAE = 43
    Luxembourg = 44
    Kuwait = 45
    HongKong = 46
    Colombia = 47
    Japan = 48
    Andorra = 49
    Azerbaijan = 50
    Bulgaria = 51
    Cuba = 52
    CzechRepublic = 53
    Estonia = 54
    Georgia = 55
    India = 56
    Israel = 57
    Jamaica = 58
    Latvia = 59
    Lithuania = 60
    Macau = 61
    Malaysia = 62
    Nepal = 63
    NewCaledonia = 64
    Nigeria = 65
    NorthernIreland = 66
    PapuaNewGuinea = 67
    Philippines = 68
    Qatar = 69
    Romania = 70
    Scotland = 71
    Serbia = 72
    Slovenia = 73
    Taiwan = 74
    Ukraine = 75
    Venezuela = 76
    Wales = 77


class CarLocation(Enum):

    NONE = 0
    Track = 1
    Pitlane = 2
    PitEntry = 3
    PitExit = 4


class DriverCategory(Enum):

    bronze = 0
    Silver = 1
    Gold = 2
    Platium = 3


class CupCategory(Enum):

    Pro = 0
    ProAm = 1
    Am = 2
    Silver = 3
    National = 4


class SessionType(Enum):

    Practice = 0
    Qualifying = 4
    Superpole = 9
    Race = 10
    Hotlap = 11
    Hotstint = 12
    HotlapSuperpole = 13
    Replay = 14
    NONE = auto()


class SessionPhase(Enum):

    NONE = auto()
    Starting = 1
    PreFormation = 2
    FormationLap = 3
    PreSession = 4
    Session = 5
    SessionOver = 6
    PostSession = 7
    ResultUI = 8


class LapType(Enum):

    ERROR = 0
    OutLap = 1
    Regular = 2
    InLap = 3


class LapInfo:

    def __init__(self, cur: Cursor):

        self.lap_time_ms = cur.read_u32()
        self.car_index = cur.read_u16()
        self.driver_index = cur.read_u16()

        split_count = cur.read_u8()
        self.splits = []
        for _ in range(split_count):
            self.splits.append(cur.read_i32())

        self.is_invalid = cur.read_u8() > 0
        self.is_valid_for_best = cur.read_u8() > 0

        is_out_lap = cur.read_u8() > 0
        is_in_lap = cur.read_u8() > 0

        if is_out_lap:
            self.late_type = LapType.OutLap

        elif is_in_lap:
            self.late_type = LapType.InLap

        else:
            self.late_type = LapType.Regular

        for i, split in enumerate(self.splits):
            if split == 2147483647:  # Max int32 value
                self.splits[i] = 0

        if self.lap_time_ms == 2147483647:
            self.lap_time_ms = 0

        self._cur = cur

    def get_cur(self):
        cur = self._cur
        self._cur = None
        return cur


class Registration:

    def __init__(self):

        self.connection_id = -1
        self.connection_succes = False
        self.is_read_only = False
        self.error_msg = "Not Initialized yet"

    def update(self, cur: Cursor):

        self.connection_id = cur.read_i32()
        self.connection_succes = cur.read_u8() > 0
        self.is_read_only = cur.read_u8() == 0
        self.error_msg = cur.read_string()


class RealTimeUpdate:

    def __init__(self):
        self.event_index = -1
        self.session_index = -1
        self.session_type = SessionType.NONE
        self.phase = SessionPhase.NONE

        self.session_time = datetime.datetime.fromtimestamp(0)
        self.session_end_time = datetime.datetime.fromtimestamp(0)

        self.focused_car_index = -1
        self.active_camera_set = ""
        self.active_camera = ""
        self.current_hud_page = ""
        self.is_replay_playing = False
        self.replay_session_time = datetime.datetime.fromtimestamp(0)
        self.replay_remaining_time = datetime.datetime.fromtimestamp(0)

        self.time_of_day = datetime.datetime.fromtimestamp(0)
        self.ambient_temp = -1
        self.track_temp = -1
        self.clouds = -1
        self.rain_level = -1
        self.wetness = -1
        self.best_session_lap = None

    def update(self, cur: Cursor):

        self.event_index = cur.read_u16()
        self.session_index = cur.read_u16()
        self.session_type = SessionType(cur.read_u8())
        self.phase = SessionPhase(cur.read_u8())

        session_time = cur.read_f32() // 1000
        self.session_time = datetime.datetime.fromtimestamp(session_time)
        session_end_time = cur.read_f32() // 1000
        self.session_end_time = datetime.datetime.fromtimestamp(
            session_end_time)

        self.focused_car_index = cur.read_i32()
        self.active_camera_set = cur.read_string()
        self.active_camera = cur.read_string()
        self.current_hud_page = cur.read_string()
        self.is_replay_playing = cur.read_u8() > 0
        self.replay_session_time = datetime.datetime.fromtimestamp(0)
        self.replay_remaining_time = datetime.datetime.fromtimestamp(0)

        if self.is_replay_playing:
            self.replay_session_time = datetime.datetime.fromtimestamp(
                cur.read_f32() / 1000)
            self.replay_remaining_time = datetime.datetime.fromtimestamp(
                cur.read_f32() / 1000)

        self.time_of_day = datetime.datetime.fromtimestamp(
            cur.read_f32() / 1000)
        self.ambient_temp = cur.read_u8()
        self.track_temp = cur.read_u8()
        self.clouds = cur.read_u8() / 10
        self.rain_level = cur.read_u8() / 10
        self.wetness = cur.read_u8() / 10
        self.best_session_lap = LapInfo(cur)


class RealTimeCarUpdate():

    def __init__(self, cur: Cursor):

        self.car_index = cur.read_u16()
        self.driver_index = cur.read_u16()
        self.driver_count = cur.read_u8()
        self.gear = cur.read_u8()
        self.world_pos_x = cur.read_f32()
        self.world_pos_y = cur.read_f32()
        self.yaw = cur.read_f32()
        self.car_location = CarLocation(cur.read_u8())
        self.kmh = cur.read_u16()
        self.position = cur.read_u16()
        self.cup_position = cur.read_u16()
        self.track_position = cur.read_u16()
        self.spline_position = cur.read_f32()
        self.lap = cur.read_u16()
        self.delta = cur.read_i32()
        self.best_session_lap = LapInfo(cur)
        cur = self.best_session_lap.get_cur()
        self.last_lap = LapInfo(cur)
        cur = self.last_lap.get_cur()
        self.current_lap = LapInfo(cur)


class TrackData:

    def __init__(self):

        self.track_name = ""
        self.track_id = -1
        self.track_meters = -1

        self.camera_sets = {}
        self.hud_page = []

    def update(self, cur: Cursor):

        _ = cur.read_i32()  # Connection id
        self.track_name = cur.read_string()
        self.track_id = cur.read_i32()
        self.track_meters = cur.read_i32()

        self.camera_sets = {}
        camera_set_count = cur.read_u8()
        for _ in range(camera_set_count):

            camera_set_name = cur.read_string()
            self.camera_sets.update({camera_set_name: []})

            camera_count = cur.read_u8()
            for _ in range(camera_count):
                camera_name = cur.read_string()
                self.camera_sets[camera_set_name].append(camera_name)

        self.hud_page = []
        hud_page_count = cur.read_u8()
        for _ in range(hud_page_count):
            self.hud_page.append(cur.read_string())


class CarInfo:

    def __init__(self, car_index: int):

        self.car_index = car_index
        self.model_type = -1
        self.team_name = ""
        self.race_number = -1
        self.cup_category = CupCategory.National
        self.current_driver_index = -1
        self.drivers = []
        self.nationality = Nationality.Any

    def update(self, cur: Cursor):

        self.model_type = cur.read_u8()
        self.team_name = cur.read_string()
        self.race_number = cur.read_i32()
        self.cup_category = CupCategory(cur.read_u8())
        self.current_driver_index = cur.read_u8()
        self.nationality = Nationality(cur.read_u16())

        self.drivers.clear()
        driver_count = cur.read_u8()
        for _ in range(driver_count):

            driver = DriverInfo(cur)
            cur = driver.get_cur()
            self.drivers.append(driver)

    def __str__(self) -> str:

        return (f"ID: {self.car_index} Team: {self.team_name} "
                "N°: {self.race_number}")


class EntryList:

    def __init__(self):

        self.entry_list = []

    def update(self, cur: Cursor):

        self.entry_list = []

        _ = cur.read_i32()  # Connection id
        car_entry_count = cur.read_u16()
        for _ in range(car_entry_count):
            self.entry_list.append(CarInfo(cur.read_u16()))

    def update_car(self, cur: Cursor):
        car_id = cur.read_u16()

        car_info = None
        for car in self.entry_list:
            if car.car_index == car_id:
                car_info = car

        if not car_info:
            print("Entry list update for unknow car index")
            return

        car_info.update(cur)


class DriverInfo():

    def __init__(self, cur: Cursor):
        self.first_name = cur.read_string()
        self.last_name = cur.read_string()
        self.short_name = cur.read_string()
        self.category = DriverCategory(cur.read_u8())
        self.nationality = Nationality(cur.read_u16())

        self._cur = cur

    def get_cur(self) -> Cursor:
        cur = self._cur
        self._cur = None
        return cur

    def __str__(self) -> str:

        return f"Name: {self.first_name} {self.last_name}"


class Leaderboard:

    def __init__(self, socket, acc_ip, acc_port):
        self.registration = Registration()
        self.session = RealTimeUpdate()
        self.track = TrackData()
        self.entry_list = EntryList()
        self.work = True

        self.leaderboard_data = {}

        self._socket = socket
        self._ip = acc_ip
        self._port = acc_port
        self._last_time_requested = datetime.datetime.now()

    def update(self):

        data, addr = self._socket.recvfrom(2048)
        # print(data, addr)  # Debug

        cur = Cursor(data)
        packet_type = cur.read_u8()

        if packet_type == 1:
            print("Registration Result")
            self.registration.update(cur)

            self.request_track_data()
            self.request_entry_list()

        elif packet_type == 2:
            # print("Real Time Update")
            self.session.update(cur)

        elif packet_type == 3:
            # print("Real Time Car Update")
            car_update = RealTimeCarUpdate(cur)

            is_unkown = True
            for car in self.entry_list.entry_list:
                if car_update.car_index == car.car_index:
                    is_unkown = False

            last_request = datetime.datetime.now() - self._last_time_requested
            if is_unkown and last_request.total_seconds() >= 1:
                self.request_entry_list()
                self._last_time_requested = datetime.datetime.now()

            elif not is_unkown:
                self.update_leaderboard(car_update)

        elif packet_type == 4:
            print("Entry List")
            self.entry_list.update(cur)
            self.add_to_leaderboard()

        elif packet_type == 5:
            print("Track Data")
            self.track.update(cur)

        elif packet_type == 6:
            print("Entry List Car")
            self.entry_list.update_car(cur)

        elif packet_type == 7:
            # print("Broadcasting Event => Don't care (:")
            pass

    def add_to_leaderboard(self) -> None:

        self.leaderboard_data.clear()

        for entry in self.entry_list.entry_list:
            self.leaderboard_data.update({entry.car_index: {}})

    def update_leaderboard(self, data: RealTimeCarUpdate) -> None:

        entry_list = self.entry_list.entry_list

        entry_index = -1
        for index, entry in enumerate(entry_list):
            if entry.car_index == data.car_index:
                entry_index = index

        if entry_index >= 0 and len(entry_list[entry_index].drivers) > 0:
            car_info = entry_list[entry_index]
            drivers = car_info.drivers

            race_number = car_info.race_number
            cup_category = car_info.cup_category
            model_type = car_info.model_type
            team_name = car_info.team_name
            first_name = drivers[data.driver_index].first_name
            last_name = drivers[data.driver_index].last_name

        else:
            race_number = -1
            cup_category = CupCategory.National
            model_type = -1
            team_name = "Team Name"
            first_name = "First Name"
            last_name = "Last Name"

        self.leaderboard_data[data.car_index].update({
            "position": data.position,
            "car number": race_number,
            "cup category": cup_category.name,
            "cup position": data.cup_position,
            "manufacturer": model_type,
            "team": team_name,
            "driver": {
                "first name": first_name,
                "last name": last_name,
            },
            "lap": data.lap,
            "current lap": data.current_lap.lap_time_ms,
            "last lap": data.last_lap.lap_time_ms,
            "best session lap": data.best_session_lap.lap_time_ms,
            "sectors": data.last_lap.splits,
            "car location": data.car_location.name
        })

    def connect(self, name: str, psw: str, speed: int, cmd_psw: str) -> None:

        msg = b""
        msg += write_int(1, "u8")
        msg += write_int(4, "u8")
        msg += write_str(name)
        msg += write_str(psw)
        msg += write_int(speed, "i32")
        msg += write_str(cmd_psw)

        print(f"Request Connection: {list(msg)}")
        self._socket.sendto(msg, (self._ip, self._port))

    def disconnect(self) -> None:

        msg = b""
        msg += write_int(9, "u8")

        print(f"Disconnect request: {list(msg)}")
        self._socket.sendto(msg, (self._ip, self._port))

    def request_entry_list(self) -> None:

        c_id = self.registration.connection_id

        if c_id != -1:

            msg = b""
            msg += write_int(10, "u8")
            msg += write_int(c_id, "i32")

            print(f"Request Entry List: {list(msg)}")
            self._socket.sendto(msg, (self._ip, self._port))

        else:
            print("no id yet can't send entry list request !")

    def request_track_data(self) -> None:

        c_id = self.registration.connection_id

        msg = b""
        msg += write_int(11, "u8")
        msg += write_int(c_id, "i32")

        print(f"Request Track Data: {list(msg)}")
        self._socket.sendto(msg, (self._ip, self._port))
