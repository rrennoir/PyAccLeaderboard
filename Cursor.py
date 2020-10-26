import sys


class Cursor:

    def __init__(self, byte: bytes):
        self._cursor = 0
        self._byte_array = byte

    def read_u8(self) -> int:

        data = self._byte_array[self._cursor: self._cursor + 1]
        self._cursor += 1

        return int.from_bytes(data, byteorder=sys.byteorder, signed=False)

    def read_u16(self) -> int:

        data = self._byte_array[self._cursor: self._cursor + 2]
        self._cursor += 2

        return int.from_bytes(data, byteorder=sys.byteorder, signed=False)

    def read_u32(self) -> int:

        data = self._byte_array[self._cursor: self._cursor + 4]
        self._cursor += 4

        return int.from_bytes(data, byteorder=sys.byteorder, signed=False)

    def read_i8(self) -> int:

        data = self._byte_array[self._cursor: self._cursor + 1]
        self._cursor += 1

        return int.from_bytes(data, byteorder=sys.byteorder, signed=True)

    def read_i16(self) -> int:

        data = self._byte_array[self._cursor: self._cursor + 2]
        self._cursor += 2

        return int.from_bytes(data, byteorder=sys.byteorder, signed=True)

    def read_i32(self) -> int:

        data = self._byte_array[self._cursor: self._cursor + 4]
        self._cursor += 4

        return int.from_bytes(data, byteorder=sys.byteorder, signed=True)

    def read_f32(self) -> float:

        data = self._byte_array[self._cursor: self._cursor + 4]
        a = data.hex()
        self._cursor += 4

        return float.fromhex(data.hex())

    def read_string(self) -> str:

        lenght = self.read_u16()

        string = self._byte_array[self._cursor: self._cursor + lenght]
        self._cursor += lenght

        return string.decode("utf-8")
