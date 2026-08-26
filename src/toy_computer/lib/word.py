from __future__ import annotations

from .exception import ToyException
from .helpers import strip_hex


class Word:
    @staticmethod
    def make_from_hex(digits: str) -> Word:
        """
        Makes a word from hexadecimal digits.
        """
        data = int(digits, 16) & 0xFFFF
        return Word.make_from_unsigned_value(data)

    @staticmethod
    def make_from_unsigned_value(data: int) -> Word:
        """
        Makes a word from data value.
        """
        return Word(bytes([(data & 0xFF00) >> 8, data & 0xFF]))

    @staticmethod
    def make_from_signed_value(value: int) -> Word:
        """
        Makes a word from a signed value in two's complement.
        """
        low, high = -(2**15), 2**15 - 1
        if value < low or value > high:
            raise ToyException(
                f"Signed value {hex(value)} outside of range "
                f"from {hex(low)} to {hex(high)}."
            )

        result = (~(abs(value) - 1)) & 0xFFFF if value < 0 else value & 0xFFFF
        return Word(bytes([(result & 0xFF00) >> 8, result & 0xFF]))

    def __init__(self, data: bytes) -> None:
        if len(data) != 2:
            raise ToyException(f"Tried to initialize a word with bytes {data}.")
        self._data = bytes(data)

    def __and__(self, other: Word) -> Word:
        return Word(bytes([a & b for a, b in zip(self._data, other._data)]))

    def __xor__(self, other: Word) -> Word:
        return Word(bytes([a ^ b for a, b in zip(self._data, other._data)]))

    def __lshift__(self, bits: int) -> Word:
        return Word.make_from_unsigned_value((self.data << bits) & 0xFFFF)

    def __rshift__(self, bits: int) -> Word:
        return Word.make_from_unsigned_value((self.data & 0xFFFF) >> bits)

    def __str__(self) -> str:
        return self._data.hex()

    def __hash__(self) -> int:
        return hash((self._data[0] << 8) + self._data[1])

    def __eq__(self, value: object) -> bool:
        return isinstance(value, Word) and all(
            a == b for a, b in zip(self._data, value._data)
        )

    def bit_value(self, index: int) -> bool:
        """
        Whether bit `index` is on.

        `index` can take on a value from 0 to 15 for the least to
        most significant bit respectively.
        """
        b_index = 1 - index // 8
        if b_index < 0 or b_index > 1:
            raise ToyException(f"Trying to access bit {b_index} of word {self}.")
        bit = index % 8
        return self._data[b_index] & (1 << bit) != 0

    @property
    def as_bytes(self) -> bytes:
        return bytes(self._data)

    @property
    def nibbles(self) -> tuple[int, int, int, int]:
        """
        The four nibbles that make up the word.
        """
        return (
            (self._data[0] & 0xF0) >> 4,
            self._data[0] & 0xF,
            (self._data[1] & 0xF0) >> 4,
            self._data[1] & 0xF,
        )

    @property
    def data(self) -> int:
        a, b, c, d = self.nibbles
        return (a << 12) + (b << 8) + (c << 4) + d

    @property
    def value(self) -> int:
        """
        The (signed) value stored in the word if interpreted as a two's
        complement integer.
        """
        a, b, c, d = self.nibbles
        v = (a << 12) + (b << 8) + (c << 4) + d
        if self.bit_value(15):
            return -(((v - 1) ^ 0xFFFF) & 0xFFFF)
        return v

    def update(self, data: bytes) -> None:
        if len(data) != 2:
            raise Exception  # TODO
        self._data = bytes(data)

    def decode(self) -> tuple[int, int, int, int, int]:
        """
        The values of opcode, d, s, t and addr of the data interpreted
        as a machine instruction.
        """
        opcode = (self._data[0] & 0xF0) >> 4

        d, s, t = (
            self._data[0] & 0xF,
            (self._data[1] & 0xF0) >> 4,
            self._data[1] & 0xF,
        )
        addr = self._data[1]
        return opcode, d, s, t, addr

    @property
    def binary(self) -> str:
        """
        The word in binary.
        """
        return "".join([bin(a)[2:].rjust(8, "0") for a in self._data])

    @property
    def characters(self) -> str:
        """
        The word as ascii characters.
        """

        def output(a: int) -> str:
            result = chr(a)
            if not result.isprintable():
                return "◻"
            return result

        return "".join([output(a) for a in self._data])

    @property
    def pseudocode(self) -> str:
        """
        The pseudocode for the word if interpreted as a machine instruction.
        """
        opcode, d, s, t, addr = self.decode()

        match opcode:
            case 0x0:
                return "halt"
            case 0x1:
                return f"R[{strip_hex(d)}] <- R[{strip_hex(s)}] + R[{strip_hex(t)}]"
            case 0x2:
                return f"R[{strip_hex(d)}] <- R[{strip_hex(s)}] - R[{strip_hex(t)}]"
            case 0x3:
                return f"R[{strip_hex(d)}] <- R[{strip_hex(s)}] & R[{strip_hex(t)}]"
            case 0x4:
                return f"R[{strip_hex(d)}] <- R[{strip_hex(s)}] ^ R[{strip_hex(t)}]"
            case 0x5:
                return f"R[{strip_hex(d)}] <- R[{strip_hex(s)}] << R[{strip_hex(t)}]"
            case 0x6:
                return f"R[{strip_hex(d)}] <- R[{strip_hex(s)}] >> R[{strip_hex(t)}]"
            case 0x7:
                return f"R[{strip_hex(d)}] <- {strip_hex(addr, 2)}"
            case 0x8:
                return f"R[{strip_hex(d)}] <- M[{strip_hex(addr, 2)}]"
            case 0x9:
                return f"M[{strip_hex(addr, 2)}] <- R[{strip_hex(d)}]"
            case 0xA:
                if s:
                    match s:
                        case 0x1:
                            return f"R[{strip_hex(d)}] <- stdin (signed)"
                        case 0x2:
                            return f"R[{strip_hex(d)}] <- stdin (unsigned)"
                        case 0x3:
                            return f"M[R[{d}]...] <- stdin"
                        case 0x4:
                            return f"R[{strip_hex(d)}] <- random"
                return f"R[{strip_hex(d)}] <- M[R[{strip_hex(t)}]]"
            case 0xB:
                if s:
                    match s:
                        case 0x1:
                            return f"stdout <- R[{strip_hex(d)}] (den)"
                        case 0x2:
                            return f"stdout <- R[{strip_hex(d)}] (u_den)"
                        case 0x3:
                            return f"stdout <- R[{strip_hex(d)}] (bin)"
                        case 0x4:
                            return f"stdout <- R[{strip_hex(d)}] (u_bin)"
                        case 0x5:
                            return f"stdout <- R[{strip_hex(d)}] (oct)"
                        case 0x6:
                            return f"stdout <- R[{strip_hex(d)}] (u_oct)"
                        case 0x7:
                            return f"stdout <- R[{strip_hex(d)}] (hex)"
                        case 0x8:
                            return f"stdout <- R[{strip_hex(d)}] (u_hex)"
                        case 0x9:
                            return f"stdout <- R[{strip_hex(d)}] (pattern)"
                        case 0xA:
                            return f"stdout <- R[{strip_hex(d)}] (char)"
                        case 0xB:
                            return "stdout <- line"
                        case 0xC:
                            return f"stdout <- M[R[{strip_hex(d)}]...]"
                return f"M[R[{strip_hex(t)}]] <- R[{strip_hex(d)}]"
            case 0xC:
                return f"if R[{strip_hex(d)}] = 0 PC <- {strip_hex(addr, 2)}"
            case 0xD:
                return f"if R[{strip_hex(d)}] > 0 PC <- {strip_hex(addr, 2)}"
            case 0xE:
                return f"PC <- R[{strip_hex(d)}]"
            case 0xF:
                return f"R[{strip_hex(d)}] <- PC; PC <- {strip_hex(addr, 2)}"
            case _:
                return ""
