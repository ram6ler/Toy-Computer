from __future__ import annotations
import re
from random import randrange
from .word import Word
from .exception import ToyException
from .helpers import stdin_get_int, stdin_get_int_u, strip_hex


def data_from_machine_code(code: str) -> tuple[int, list[int]]:
    lines = [
        stripped
        for line in code.split("\n")
        if (stripped := line.split(";")[0].strip().lower())
    ]
    pc = 0
    instructions = [0 for _ in range(256)]
    for line in lines:
        m = re.match(r"^pc\s*:\s*([0-9a-f]{1,2})$", line)
        if m is None:
            m = re.match(r"^([0-9a-f]{1,2})\s*:\s*([0-9a-f]{1,4})$", line)
            if m is None:
                raise ToyException(f"Bad code: '{line}'.")
            addr = int(m.group(1), base=16)
            data = int(m.group(2), base=16)
            instructions[addr] = data
        else:
            pc = int(m.group(1), base=16)
    if len(instructions) > 256:
        raise ToyException(f"RAM overflow: {len(instructions)} instructions.")
    return pc, instructions


class Computer:
    @staticmethod
    def from_machine_code(code: str) -> Computer:
        pc, instructions = data_from_machine_code(code)
        return Computer(pc=pc, ram=instructions)

    def __init__(
        self,
        pc=0,
        registers: list[int] = [],
        ram: list[int] = [],
    ) -> None:
        self._initial_pc = pc
        self.pc = pc
        self.registers = [
            Word.make_from_hex("0000")
            if i >= len(registers)
            else Word.make_from_unsigned_value(registers[i])
            for i in range(16)
        ]
        self.ram = [
            Word.make_from_hex("0000")
            if i >= len(ram)
            else Word.make_from_unsigned_value(ram[i])
            for i in range(256)
        ]
        self._halted = False

    def fetch_and_execute(self) -> bool:
        """
        Fetches and executes an instruction; returns whether
        there are more instructions to execute.
        """

        instruction = self.ram[self.pc]
        opcode, d, s, t, addr = instruction.decode()
        self.pc = (self.pc + 1) % 256

        def error_message(message: str) -> str:
            return f"[{strip_hex(self.pc)}] {instruction}: {message}"

        match opcode:
            case 0x0:
                # halt
                self._halted = True

            case 0x1:
                # add R[d] <- R[s] + R[t]
                a, b = self.registers[s].value, self.registers[t].value
                result = Word.make_from_signed_value(a + b)
                self.registers[d].update(result.as_bytes)

            case 0x2:
                # subtract R[d] <- R[s] - R[t]
                a, b = self.registers[s].value, self.registers[t].value
                result = Word.make_from_signed_value(a - b)
                self.registers[d].update(result.as_bytes)

            case 0x3:
                # bitwise and R[d] <- R[s] & R[t]
                a, b = self.registers[s], self.registers[t]
                result = a & b
                self.registers[d].update(result.as_bytes)

            case 0x4:
                # bitwise xor R[d] <- R[s] ^ R[d]
                a, b = self.registers[s], self.registers[t]
                result = a ^ b
                self.registers[d].update(result.as_bytes)

            case 0x5:
                # left shift R[d] <- R[s] << R[t]
                a, b = self.registers[s], self.registers[t].value
                if b < 0:
                    raise ToyException(
                        error_message(
                            f"Attempted R[{strip_hex(d)}] <- "
                            f"R[{strip_hex(s)}] << R[{strip_hex(t)}] "
                            f"where R[{t}] = {b}."
                        )
                    )
                result = a << b
                self.registers[d].update(result.as_bytes)

            case 0x6:
                # right shift R[d] <- R[s] >> R[t]
                a, b = self.registers[s], self.registers[t].value
                if b < 0:
                    raise ToyException(
                        error_message(
                            f"Attempted R[{strip_hex(d)}] <- "
                            f"R[{strip_hex(s)}] >> R[{strip_hex(t)}] "
                            f"where R[{t}] = {b}."
                        )
                    )
                result = a >> b
                self.registers[d].update(result.as_bytes)

            case 0x7:
                # load address R[d] <- addr
                self.registers[d].update(bytes([0, addr]))

            case 0x8:
                # load R[d] <- M[addr]
                self.registers[d].update(self.ram[addr].as_bytes)

            case 0x9:
                # store M[addr] <- R[d]
                self.ram[addr].update(self.registers[d].as_bytes)

            case 0xA:
                match s:
                    case 0x0:
                        # load indirect R[d] <- M[R[t]]
                        i = self.registers[t].value
                        if i < 0 or i > 255:
                            raise ToyException(
                                error_message(
                                    f"Attempted R[{strip_hex(d)}] <- M[R[{strip_hex(t)}]] "
                                    f"where R[{strip_hex(t)}] = {hex(i)}"
                                )
                            )
                        self.registers[d].update(self.ram[i].as_bytes)

                    # Extension: stdin
                    case 0x1:
                        # input
                        response = Word.make_from_signed_value(
                            stdin_get_int()
                        ).as_bytes
                        self.registers[d].update(response)

                    case 0x2:
                        # input_u
                        response = Word.make_from_unsigned_value(
                            abs(stdin_get_int_u()) & 0xFFFF
                        ).as_bytes
                        self.registers[d].update(response)

                    case 0x3:
                        # input_str
                        i = self.registers[d].value
                        if i < 0 or i > 255:
                            raise ToyException(
                                error_message(
                                    f"Attempted to write to address "
                                    f"R[{strip_hex(d)}] = {strip_hex(i)}."
                                )
                            )
                        string = (
                            input()
                            .replace(r"\\", "\\")
                            .replace(r"\t", "\t")
                            .replace(r"\n", "\n")
                            .replace(r"\"", '"')
                        )
                        terminated = False
                        for j in range(0, len(string), 2):
                            a = ord(string[j]) & 0xFF
                            k = j + 1
                            if k == len(string):
                                b = 0
                                terminated = True
                            else:
                                b = ord(string[k]) & 0xFF
                            self.ram[i].update(bytes([a, b]))
                            i += 1
                            if i > 256:
                                raise ToyException(
                                    error_message(
                                        "Memory overflow while attempting "
                                        f"to read in '{string}'."
                                    )
                                )
                        if not terminated:
                            self.ram[i].update(bytes([0, 0]))

                    case 0x4:
                        # rand
                        self.registers[d].update(
                            Word.make_from_unsigned_value(
                                randrange(2**16)
                            ).as_bytes
                        )

                    case _:
                        raise ToyException(
                            error_message(
                                f"Input not implemented for for s={strip_hex(s)}."
                            )
                        )

            case 0xB:
                value = self.registers[d].value
                data = self.registers[d].data
                match s:
                    case 0x0:
                        # store indirect M[R[t]] <- R[d]
                        i = self.registers[t].value
                        if i < 0 or i > 255:
                            raise ToyException(
                                error_message(
                                    f"Attempted M[R[{strip_hex(t)}]] <- R[{strip_hex(d)}] "
                                    f"where R[{strip_hex(t)}] = {hex(t)}."
                                )
                            )

                        self.ram[i].update(self.registers[d].as_bytes)

                        # Extension: stdout
                    case 0x1:
                        # den
                        print(value, end="")

                    case 0x2:
                        # u_den
                        print(data, end="")

                    case 0x3:
                        # bin
                        print(bin(value).replace("0b", ""), end="")

                    case 0x4:
                        # u_bin
                        print(bin(data).replace("0b", ""), end="")

                    case 0x5:
                        # oct
                        print(oct(value).replace("0o", ""), end="")

                    case 0x6:
                        # u_oct
                        print(oct(data).replace("0o", ""), end="")

                    case 0x7:
                        # hex
                        print(hex(value).replace("0x", ""), end="")

                    case 0x8:
                        # u_hex
                        print(hex(data).replace("0x", ""), end="")

                    case 0x9:
                        # pattern
                        print(
                            bin(data)[2:]
                            .rjust(16, "0")
                            .replace("1", "█")
                            .replace("0", " "),
                            end="",
                        )

                    case 0xA:
                        # char
                        first, second = (
                            chr((data & 0xFF00) >> 8),
                            chr(data & (0xFF)),
                        )
                        result = ""
                        if first.isprintable:
                            result += first
                        if second.isprintable:
                            result += second
                        print(result, end="")

                    case 0xB:
                        # line
                        print()

                    case 0xC:
                        # write
                        i = data
                        terminated = False
                        while not terminated:
                            if i >= 256:
                                raise ToyException(
                                    error_message(
                                        "Memory overflow for unterminated string."
                                    )
                                )
                            a = (self.ram[i].data & 0xFF00) >> 8
                            if a:
                                print(chr(a), end="")
                                b = self.ram[i].data & 0xFF
                                if b:
                                    print(chr(b), end="")
                                else:
                                    terminated = True
                            else:
                                terminated = True
                            i += 1

            case 0xC:  # branch zero if R[d] = 0 PC <- addr
                if self.registers[d].value == 0:
                    self.pc = addr

            case 0xD:  # branch positive if R[d] > 0 PC <- addr
                if self.registers[d].value > 0:
                    self.pc = addr

            case 0xE:  # jump register PC <- R[d]
                i = self.registers[d].value
                if i < 0 or i > 255:
                    raise ToyException(
                        error_message(
                            f"Attempted PC <- R[{strip_hex(d)}], which is {strip_hex(i)}."
                        )
                    )
                self.pc = i

            case 0xF:  # jump & link R[d] <- PC; PC <- addr
                self.registers[d].update(bytes([0, self.pc]))
                self.pc = addr
        return not self._halted

    def run(self) -> None:
        """
        Runs the program.
        """
        while not self._halted:
            self.fetch_and_execute()

    def reset(self) -> None:
        """
        Clears the registers and resets the PC.
        """
        for r in self.registers:
            r.update(bytes([0, 0]))
        self.pc = self._initial_pc
        self._halted = False

    def clear(self) -> None:
        """
        Clears the registers, PC and RAM.
        """
        self._initial_pc = 0
        self.reset()
        for r in self.ram:
            r.update(bytes([0, 0]))

    def load(self, code: str) -> None:
        """
        Clears the computer and loads program specified by `code`.
        """
        self.reset()
        pc, instructions = data_from_machine_code(code)
        self._initial_pc = self.pc = pc
        for i, instruction in enumerate(instructions):
            left_byte = (instruction & 0xFF00) >> 8
            right_byte = instruction & 0xFF
            self.ram[i].update(bytes([left_byte, right_byte]))

    @property
    def dump(self) -> str:
        """
        Returns a representation of the computer's state, including
        the values in the registers and the RAM.
        """
        result = ""
        result += (
            f"           {'   '.join(f'_{hex(i)[2:]}' for i in range(16))}\n"
        )
        for i in range(16):
            result += f"%{hex(i)[2:]} {self.registers[i]} {hex(i)[2:]}_ "
            result += " ".join(f"{self.ram[i * 16 + j]}" for j in range(16))
            result += "\n"
        result += (
            f"\nPC: {hex(self.pc)[2:].rjust(2, '0')} "
            f"({hex(self._initial_pc)[2:].rjust(2, '0')})\n"
            f"CIR: {self.ram[self.pc]}"
        )
        return result

    @property
    def breakdown(self) -> str:
        """
        Returns a breakdown of the values in the RAM, including
        interpretations as ascii, values and instructions.
        """
        result = f"PC: {hex(self.pc)[2:].rjust(2, '0')}\n"
        for i, data in enumerate(self.ram):
            if data == Word.make_from_unsigned_value(0):
                continue
            r = self.ram[i]
            addr = hex(i)[2:].rjust(2, "0")
            data = str(self.ram[i])
            binary = r.binary
            value = r.value
            characters = r.characters
            pseudocode = r.pseudocode
            result += (
                f"{addr}: {data}; {binary} "
                f"{f'{value:,} '.rjust(8)}"
                f"{characters} {pseudocode}"
            )
            if i == self.pc:
                result += " (*)"
            result += "\n"

        return result
