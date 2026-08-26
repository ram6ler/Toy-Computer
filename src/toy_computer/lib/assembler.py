from .language import expressions, SUBSTITUTION, STRING_EXPRESSION
from .word import Word
from .helpers import parse_to_int
from .exception import ToyException


class Assembled:
    def __init__(
        self,
        assembly: str,
        lookup_table: dict[str, int],
        machine_code: str,
    ) -> None:
        self._assembly = assembly
        self._lookup_table = lookup_table
        self._machine_code = machine_code

    @property
    def assembly(self) -> str:
        width = max(len(line) for line in self._assembly.split("\n"))
        result = "-" * width
        result += f"\n{self._assembly}\n"
        result += "-" * width + "\n"
        return result

    @property
    def lookup_table(self) -> str:
        result = ""
        if not self._lookup_table:
            return result
        width = max(len(k) for k in self._lookup_table)
        result += f".-{'-' * width}-----.\n"
        for k in sorted(self._lookup_table):
            result += (
                f"| {k.rjust(width)}: "
                f"{hex(self._lookup_table[k])[2:].rjust(2, '0')} |\n"
            )
        result += f"'-{'-' * width}-----'\n"
        return result

    @property
    def machine_code(self) -> str:
        return self._machine_code


def get_lines(assembly: str) -> list[str]:
    clean_lines = list[str]()
    for line in assembly.split("\n"):
        m = STRING_EXPRESSION.search(line)
        if m:
            line = f"{line[: m.start()]}<STRING>{line[m.end() :]}"

        if "//" in line:
            line = line.split("//")[0].strip()

        if ":" in line:
            while ":" in line:
                lab, *rest = line.split(":")
                clean_lines.append(f"{lab.strip()}:")
                line = ":".join(rest)
        line = line.strip()
        if m:
            line = line.replace("<STRING>", m.group(0))
        if line:
            clean_lines.append(line)
    return clean_lines


def get_format_value(fmt: str) -> str:
    """
    Determines the value of the S nibble for output
    extensions to instruction B (store indirect).
    """
    match fmt:
        case ".den":
            return "1"
        case ".u_den":
            return "2"
        case ".bin":
            return "3"
        case ".u_bin":
            return "4"
        case ".oct":
            return "5"
        case ".u_oct":
            return "6"
        case ".hex":
            return "7"
        case ".u_hex":
            return "8"
        case ".pattern":
            return "9"
        case ".char":
            return "a"
    raise NotImplementedError()


def load(register: str, val: str) -> list[str]:
    """
    Loads value `val` to a register `register`.

    Multiple instructions are inserted if `val` takes
    up more than a byte.
    """

    def hex_two(x: int) -> str:
        return hex(x)[2:].rjust(2, "0")

    i = parse_to_int(val)
    if 0 <= i < 256:
        return [f"7{register}{hex_two(i)}"]
    a, b = hex_two((i & 0xFF00) >> 8), hex_two(i & 0xFF)
    return [
        # %f <- a
        f"7f{a}",
        # %e <- 8
        "7e08",
        # %f <- %f << %e
        "5ffe",
        # %e <- b
        f"7e{b}",
        # R[register] <- %e ^ %f
        f"4{register}ef",
    ]


def assemble(assembly: str) -> Assembled:
    """
    Parses assembly code and returns an instance of `Assembled`,
    which contains the resulting machine code and lookup table.
    """
    lines = get_lines(assembly)
    pc = [0]

    def update_pc(val: int) -> None:
        pc[0] = val

    def get_pc() -> str:
        return hex(pc[0])[2:].rjust(2, "0")

    ram = list[str]()
    lookup_table = dict[str, int]()

    for line in lines:
        if m := expressions[".main"].match(line):
            update_pc(len(ram))
            continue

        if m := expressions[".input d"].match(line):
            d = m.group("d")
            ram.append(
                # R[d] <- input
                f"a{d}10",
            )
            continue

        if m := expressions[".input [t]"].match(line):
            t = m.group("t")
            ram.extend(
                [
                    # %f <- input
                    "af10",
                    # M[R[t]] <- %f
                    f"bf0{t}",
                ]
            )
            continue

        if m := expressions[".input [lab]"].match(line):
            lab = m.group("lab")
            ram.extend(
                [
                    # %f <- input
                    "af10",
                    # %e <- lab
                    f"7e<{lab}>",
                    # M[%e] <- %f
                    "bf0e",
                ]
            )
            continue

        if m := expressions[".input_u d"].match(line):
            d = m.group("d")
            ram.append(
                # R[d] <- input_dat
                f"a{d}20",
            )
            continue

        if m := expressions[".input_u [t]"].match(line):
            t = m.group("t")
            ram.extend(
                [
                    # %f <- input
                    "af20",
                    # M[R[t]] <- %f
                    f"bf0{t}",
                ]
            )
            continue

        if m := expressions[".input_u [lab]"].match(line):
            lab = m.group("lab")
            ram.extend(
                [
                    # %f <- input
                    "af20",
                    # %e <- lab
                    f"7e<{lab}>",
                    # M[%e] <- %f
                    "bf0e",
                ]
            )
            continue

        if m := expressions[".input_str [d]"].match(line):
            d = m.group("d")
            ram.append(
                # M[R[d]...] <- input_str
                f"a{d}30",
            )
            continue

        if m := expressions[".input_str [lab]"].match(line):
            lab = m.group("lab")
            ram.extend(
                [
                    # %f <- lab
                    f"7f<{lab}>",
                    # M[%f...] <- input_str
                    "af30",
                ]
            )
            continue

        if m := expressions[".rand d"].match(line):
            d = m.group("d")
            ram.append(
                # R[d] <- rand
                f"a{d}40",
            )
            continue

        if m := expressions[".rand [t]"].match(line):
            t = m.group("t")
            ram.extend(
                [
                    # %f <- rand
                    "af40",
                    # M[R[t]] <- %f
                    f"bf0{t}",
                ]
            )
            continue

        if m := expressions[".rand [lab]"].match(line):
            lab = m.group("lab")
            ram.extend(
                [
                    # %f <- rand
                    "af40",
                    # %e <- lab
                    f"7e<{lab}>",
                    # M[R[e]] <- %f
                    "bf0e",
                ]
            )
            continue

        if m := expressions["fmt d"].match(line):
            fmt = m.group("fmt")
            d = m.group("d")
            s = get_format_value(fmt)
            ram.append(
                # fmt <- R[d]
                f"b{d}{s}0",
            )
            continue

        if m := expressions["fmt [t]"].match(line):
            fmt = m.group("fmt")
            t = m.group("t")
            s = get_format_value(fmt)
            ram.extend(
                [
                    # %f <- M[R[T]]
                    f"af0{t}",
                    # fmt <- %f
                    f"bf{s}0",
                ]
            )
            continue

        if m := expressions["fmt [lab]"].match(line):
            fmt = m.group("fmt")
            lab = m.group("lab")
            s = get_format_value(fmt)
            ram.extend(
                [
                    # %f <- lab
                    f"7f<{lab}>",
                    # %e <- M[%f]
                    "ae0f",
                    # fmt <- %e
                    f"be{s}0",
                ]
            )
            continue

        if m := expressions[".line"].match(line):
            ram.append(
                # line
                "b0b0",
            )
            continue

        if m := expressions[".write [d]"].match(line):
            d = m.group("d")
            ram.append(
                # write <- M[R[d]...]
                f"b{d}c0",
            )
            continue

        if m := expressions[".write [lab]"].match(line):
            lab = m.group("lab")
            ram.extend(
                [
                    # %f <- lab
                    f"7f<{lab}>",
                    # write <- M[%f...]
                    "bfc0",
                ]
            )
            continue

        if m := expressions["lab:"].match(line):
            lab = m.group("lab")
            lookup_table[lab] = len(ram)
            continue

        if m := expressions[".word"].match(line):
            ram.append("0000")
            continue

        if m := expressions[".data data"].match(line):
            data = m.group("data")
            for datum in [datum.strip() for datum in data.split(",")]:
                try:
                    i = parse_to_int(datum)
                except ValueError:
                    raise ToyException(f"Parse error:\n'{datum}' in '{line}'.")
                ram.append(
                    # datum
                    str(Word.make_from_signed_value(i)),
                )
            continue

        if m := expressions[".u_data data"].match(line):
            data = m.group("data")
            for datum in [datum.strip() for datum in data.split(",")]:
                try:
                    i = parse_to_int(datum)
                except ValueError:
                    raise ToyException(f"Parse error:\n'{datum}' in '{line}'.")
                ram.append(
                    # datum
                    str(Word.make_from_unsigned_value(i)),
                )
            continue

        if m := expressions[".stack val"].match(line):
            val = m.group("val")
            ram.extend(
                ["0000" for _ in range(parse_to_int(val) + 1)],
            )
            continue

        if m := expressions["push d lab"].match(line):
            d = m.group("d")
            lab = m.group("lab")
            ram.extend(
                [
                    # %f <- lab
                    f"7f<{lab}>",
                    # %e <- M[%f]
                    "ae0f",
                    # %d <- 01
                    "7d01",
                    # %e <- %d + %e
                    "1ede",
                    # %d <- %e + %f
                    "1def",
                    # M[%d] <- R[d]
                    f"b{d}0d",
                    # M[%f] <- %e
                    "be0f",
                ]
            )
            continue

        if m := expressions["pop d lab"].match(line):
            d = m.group("d")
            lab = m.group("lab")
            ram.extend(
                [
                    # %f <- lab
                    f"7f<{lab}>",
                    # %e <- M[%f]
                    "ae0f",
                    # %d <- %f + %e
                    "1dfe",
                    # R[d] <- M[%d]
                    f"a{d}0d",
                    # %d <- 01
                    "7d01",
                    # %e <- %e 1 %d
                    "2eed",
                    # M[%f] <- %e
                    "be0f",
                ]
            )
            continue

        if m := expressions["len d lab"].match(line):
            d = m.group("d")
            lab = m.group("lab")
            ram.extend(
                [
                    # %f <- lab
                    f"7f<{lab}>",
                    # R[d] <- M[%f]
                    f"a{d}0f",
                    # # %e <- 01
                    # "7e01",
                    # # R[d] <- R[d] - %e
                    # f"2{d}{d}e",
                ]
            )
            continue

        if m := expressions[".ascii ..."].match(line):
            string = (
                m.group("string")
                .replace(r"\\", "\\")
                .replace(r"\t", "\t")
                .replace(r"\n", "\n")
                .replace(r"\"", '"')
            )
            terminated = False
            for i in range(0, len(string), 2):
                datum = (ord(string[i]) & 0xFF) << 8
                j = i + 1
                if j == len(string):
                    terminated = True
                else:
                    datum |= ord(string[j]) & 0xFF
                ram.append(
                    # character pair
                    str(Word.make_from_unsigned_value(datum)),
                )
            if not terminated:
                ram.append(
                    # terminator
                    "0000",
                )
            continue

        if m := expressions["halt"].match(line):
            ram.append(
                # halt
                "0000",
            )
            continue

        if m := expressions["ld d [lab]"].match(line):
            d = m.group("d")
            lab = m.group("lab")
            ram.extend(
                [
                    # %f <- lab
                    f"7f<{lab}>",
                    # R[d] <- M[%f]
                    f"a{d}0f",
                ]
            )
            continue

        if m := expressions["ld d [t]"].match(line):
            d = m.group("d")
            t = m.group("t")
            ram.append(
                # R[d] <- M[R[t]]
                f"a{d}0{t}",
            )
            continue

        if m := expressions["st d [lab]"].match(line):
            d = m.group("d")
            lab = m.group("lab")
            ram.extend(
                [
                    # %f <- lab
                    f"7f<{lab}>",
                    # M[%f] <- R[d]
                    f"b{d}0f",
                ]
            )
            continue

        if m := expressions["st d [t]"].match(line):
            d = m.group("d")
            t = m.group("t")
            ram.append(
                # M[R[t]] <- R[d]
                f"b{d}0{t}",
            )
            continue

        if m := expressions["st val [lab]"].match(line):
            val = m.group("val")
            lab = m.group("lab")
            ram.extend(
                [
                    # %f <- val
                    *load("f", val),
                    # M[lab] <- %f
                    f"9f<{lab}>",
                ]
            )
            continue

        if m := expressions["st val [t]"].match(line):
            val = m.group("val")
            t = m.group("t")
            ram.extend(
                [
                    # %f <- val
                    *load("f", val),
                    # M[R[t]] <- %f
                    f"bf0{t}",
                ]
            )
            continue

        if m := expressions["jz d lab"].match(line):
            d = m.group("d")
            lab = m.group("lab")
            ram.append(
                # if R[d] = 0 PC <- lab
                f"c{d}<{lab}>",
            )
            continue

        if m := expressions["jp d lab"].match(line):
            d = m.group("d")
            lab = m.group("lab")
            ram.append(
                # if R[d] > 0 PC <- lab
                f"d{d}<{lab}>",
            )
            continue

        if m := expressions["jn d lab"].match(line):
            d = m.group("d")
            lab = m.group("lab")
            ram.extend(
                [
                    # %f <- 00
                    "7f00",
                    # %f <- %f ^ %d
                    f"4ff{d}",
                    # %e <- 0f
                    "7e0f",
                    # %f <- %f >> %e
                    "6ffe",
                    # if R[f] > 0 PC <- lab
                    f"df<{lab}>",
                ]
            )
            continue

        if m := expressions["je d s lab"].match(line):
            d = m.group("d")
            s = m.group("s")
            lab = m.group("lab")
            ram.extend(
                [
                    # %f <- R[d] ^ R[s]
                    f"4f{d}{s}",
                    # if %f = 0 PC <- addr
                    f"cf<{lab}>",
                ]
            )
            continue

        if m := expressions["jmp lab"].match(line):
            lab = m.group("lab")
            ram.extend(
                [
                    # %f <- lab
                    f"7f<{lab}>",
                    # PC <- R[f]
                    "ef00",
                ]
            )
            continue

        if m := expressions["call d lab"].match(line):
            d = m.group("d")
            lab = m.group("lab")
            ram.append(
                # R[d] <- PC; PC <- lab
                f"f{d}<{lab}>",
            )
            continue

        if m := expressions["ret d"].match(line):
            d = m.group("d")
            ram.append(
                # PC <- R[d]
                f"e{d}00",
            )
            continue

        if m := expressions["mv d s"].match(line):
            d = m.group("d")
            s = m.group("s")
            ram.extend(
                [
                    # R[d] <- 00
                    f"7{d}00",
                    # R[d] <- R[d] ^ R[s]
                    f"4{d}{d}{s}",
                ]
            )
            continue

        if m := expressions["mv d lab"].match(line):
            d = m.group("d")
            lab = m.group("lab")
            ram.append(
                # R[d] <- lab
                f"7{d}<{lab}>",
            )
            continue

        if m := expressions["mv d val"].match(line):
            d = m.group("d")
            val = m.group("val")
            try:
                ram.extend(
                    # R[d] <- val
                    load(d, val),
                )
            except ValueError:
                raise ToyException(f"Parse error: '{val}' in '{line}'.")
            continue

        if m := expressions["not d"].match(line):
            d = m.group("d")
            ram.extend(
                [
                    # %f <- ffff
                    *load("f", "0xffff"),
                    # R[d] < R[d] ^ %f
                    f"4{d}{d}f",
                ]
            )
            continue

        if m := expressions["op d s"].match(line):
            op = m.group("op")
            d = m.group("d")
            s = m.group("s")
            match op:
                case "and":
                    ram.append(
                        # R[d] <- R[d] & R[s]
                        f"3{d}{d}{s}",
                    )
                case "or":
                    ram.extend(
                        [
                            # %f <- R[d] & R[s]
                            f"3f{d}{s}",
                            # %e <- R[d] ^ R[s]
                            f"4e{d}{s}",
                            # R[d] <- %e ^ %f
                            f"4{d}ef",
                        ]
                    )
                case "xor":
                    ram.append(
                        # R[d] <- R[d] ^ R[s]
                        f"4{d}{d}{s}",
                    )
                case "lsh":
                    ram.append(
                        # R[d] <- R[d] << R[s]
                        f"5{d}{d}{s}",
                    )
                case "rsh":
                    ram.append(
                        # R[d] <- R[d] >> R[s]
                        f"6{d}{d}{s}",
                    )
                case "add":
                    ram.append(
                        # R[d] < R[d] + R[s]
                        f"1{d}{d}{s}",
                    )
                case "sub":
                    ram.append(
                        # R[d] <- R[d] - R[s]
                        f"2{d}{d}{s}",
                    )
                case "not":
                    ram.extend(
                        [
                            # %f <- ffff
                            *load("f", "0xffff"),
                            # R[d] <- R[s] ^ %f
                            f"4{d}{s}f",
                        ]
                    )
            continue

        if m := expressions["op d [t]"].match(line):
            op = m.group("op")
            d = m.group("d")
            t = m.group("t")
            match op:
                case "and":
                    ram.extend(
                        [
                            # %f <- M[R[t]]
                            f"af0{t}",
                            # R[d] <- R[d] & %f
                            f"3{d}{d}f",
                        ]
                    )
                case "or":
                    ram.extend(
                        [
                            # %f <- M[R[t]]
                            f"af0{t}",
                            # %e <- R[d] & %f
                            f"3f{d}f",
                            # %d <- R[d] ^ %f
                            f"4e{d}f",
                            # R[d] <- %d ^ %e
                            f"4{d}de",
                        ]
                    )
                case "xor":
                    ram.extend(
                        [
                            # %f <- M[R[t]]
                            f"af0{t}",
                            # R[d] <- R[d] ^ %f
                            f"4{d}{d}f",
                        ]
                    )
                case "lsh":
                    ram.extend(
                        [
                            # %f <- M[R[t]]
                            f"af0{t}",
                            # R[d] <- R[d] << %f
                            f"5{d}{d}f",
                        ]
                    )
                case "rsh":
                    ram.extend(
                        [
                            # %f <- M[R[t]]
                            f"af0{t}",
                            # R[d] <- R[d] >> %f
                            f"6{d}{d}f",
                        ]
                    )
                case "add":
                    ram.extend(
                        [
                            # %f <- M[R[t]]
                            f"af0{t}",
                            # R[d] < R[d] + %f
                            f"1{d}{d}%f",
                        ]
                    )
                case "sub":
                    ram.extend(
                        [
                            # %f <- M[R[t]]
                            f"af0{t}",
                            # R[d] <- R[d] - %f
                            f"2{d}{d}f",
                        ]
                    )
                case "not":
                    ram.extend(
                        [
                            # %f <- M[R[t]]
                            f"af0{t}",
                            # %e <- ffff
                            *load("e", "0xffff"),
                            # R[d] <- %f ^ %e
                            f"r{d}fe",
                        ]
                    )
            continue

        if m := expressions["op d [lab]"].match(line):
            op = m.group("op")
            d = m.group("d")
            lab = m.group("lab")
            match op:
                case "and":
                    ram.extend(
                        [
                            # %f <- M[lab]
                            f"8f<{lab}>",
                            # R[d] <- R[d] & %f
                            f"3{d}{d}f",
                        ]
                    )
                case "or":
                    ram.extend(
                        [
                            # %f <- M[lab]
                            f"8f<{lab}>",
                            # %e <- R[d] & %f
                            f"3f{d}f",
                            # %d <- R[d] ^ %f
                            f"4e{d}f",
                            # R[d] <- %d ^ %e
                            f"4{d}de",
                        ]
                    )
                case "xor":
                    ram.extend(
                        [
                            # %f <- M[lab]
                            f"8f<{lab}>",
                            # R[d] <- R[d] ^ %f
                            f"4{d}{d}f",
                        ]
                    )
                case "lsh":
                    ram.extend(
                        [
                            # %f <- M[lab]
                            f"8f<{lab}>",
                            # R[d] <- R[d] << %f
                            f"5{d}{d}f",
                        ]
                    )
                case "rsh":
                    ram.extend(
                        [
                            # %f <- M[lab]
                            f"8f<{lab}>",
                            # R[d] <- R[d] >> %f
                            f"6{d}{d}f",
                        ]
                    )
                case "add":
                    ram.extend(
                        [
                            # %f <- M[lab]
                            f"8f<{lab}>",
                            # R[d] < R[d] + %f
                            f"1{d}{d}%f",
                        ]
                    )
                case "sub":
                    ram.extend(
                        [
                            # %f <- M[lab]
                            f"8f<{lab}>",
                            # R[d] <- R[d] - %f
                            f"2{d}{d}f",
                        ]
                    )
                case "not":
                    ram.extend(
                        [
                            # %f <- M[lab]
                            f"8f<{lab}>",
                            # %e <- ffff
                            *load("e", "0xffff"),
                            # R[d] <- %f ^ %e
                            f"r{d}fe",
                        ]
                    )
            continue

        if m := expressions["op d val"].match(line):
            op = m.group("op")
            d = m.group("d")
            val = m.group("val")
            match op:
                case "and":
                    ram.extend(
                        [
                            # %f <- val
                            *load("f", val),
                            # R[d] <- R[d] & %f
                            f"3{d}{d}f",
                        ]
                    )
                case "or":
                    ram.extend(
                        [
                            # %f <- val
                            *load("f", val),
                            # %e <- R[d] & %f
                            f"3e{d}f",
                            # %f <- R[d] ^ %f
                            f"4f{d}f",
                            # R[d] <- %e ^ %f
                            f"4{d}ef",
                        ]
                    )
                case "xor":
                    ram.extend(
                        [
                            # %f <- val
                            *load("f", val),
                            # R[d] <- R[d] ^ %f
                            f"4{d}{d}f",
                        ]
                    )
                case "lsh":
                    ram.extend(
                        [
                            # %f <- val
                            *load("f", val),
                            # R[d] <- R[d] << %f
                            f"5{d}{d}f",
                        ]
                    )
                case "rsh":
                    ram.extend(
                        [
                            # %f <- val
                            *load("f", val),
                            # R[d] <- R[d] >> %f
                            f"6{d}{d}f",
                        ]
                    )
                case "add":
                    ram.extend(
                        [
                            # %f <- val
                            *load("f", val),
                            # R[d] < R[d] + %f
                            f"1{d}{d}f",
                        ]
                    )
                case "sub":
                    ram.extend(
                        [
                            # %f <- val
                            *load("f", val),
                            # R[d] <- R[d] - %f
                            f"2{d}{d}f",
                        ]
                    )
                case "not":
                    ram.extend(
                        [
                            # %d <- val
                            *load("d", val),
                            # %f <- ffff
                            *load("f", "0xffff"),
                            # R[d] <- %d ^ %f
                            f"r{d}df",
                        ]
                    )
            continue

        if m := expressions["op d s t"].match(line):
            op = m.group("op")
            d = m.group("d")
            s = m.group("s")
            t = m.group("t")
            match op:
                case "and":
                    ram.append(
                        # R[d] <- R[s] & R[t]
                        f"3{d}{s}{t}",
                    )
                case "or":
                    ram.extend(
                        [
                            # %f <- R[s] & R[t]
                            f"3f{s}{t}",
                            # %e <- R[s] ^ R[t]
                            f"4e{s}{t}",
                            # R[d] <- %e ^ %f
                            f"4{d}ef",
                        ]
                    )
                case "xor":
                    ram.append(
                        # R[d] <- R[s] ^ R[t]
                        f"4{d}{s}{t}",
                    )
                case "lsh":
                    ram.append(
                        # R[d] <- R[s] << R[t]
                        f"5{d}{s}{t}",
                    )
                case "rsh":
                    ram.append(
                        # R[d] <- R[s] >> R[t]
                        f"6{d}{s}{t}",
                    )
                case "add":
                    ram.append(
                        # R[d] < R[s] + R[t]
                        f"1{d}{s}{t}",
                    )
                case "sub":
                    ram.append(
                        # R[d] <- R[s] - R[t]
                        f"2{d}{s}{t}",
                    )
            continue

        if m := expressions["op d s [t]"].match(line):
            op = m.group("op")
            d = m.group("d")
            s = m.group("s")
            t = m.group("t")
            match op:
                case "and":
                    ram.extend(
                        [
                            # %f <- M[R[t]]
                            f"af0{t}",
                            # R[d] <- R[s] & %f
                            f"3{d}{s}f",
                        ]
                    )
                case "or":
                    ram.extend(
                        [
                            # %f <- M[R[t]]
                            f"af0{t}",
                            # %e <- R[s] & %f
                            f"3e{s}f",
                            # %d <- R[s] ^ %f
                            f"4d{s}f",
                            # R[d] <- %d ^ %e
                            f"4{d}de",
                        ]
                    )
                case "xor":
                    ram.extend(
                        [
                            # %f <- M[R[t]]
                            f"af0{t}",
                            # R[d] <- R[s] ^ %f
                            f"4{d}{s}f",
                        ]
                    )
                case "lsh":
                    ram.extend(
                        [
                            # %f <- M[R[t]]
                            f"af0{t}",
                            # R[d] <- R[s] << %f
                            f"5{d}{s}f",
                        ]
                    )
                case "rsh":
                    ram.extend(
                        [
                            # %f <- M[R[t]]
                            f"af0{t}",
                            # R[d] <- R[s] >> %f
                            f"6{d}{s}f",
                        ]
                    )
                case "add":
                    ram.extend(
                        [
                            # %f <- M[R[t]]
                            f"af0{t}",
                            # R[d] < R[s] + %f
                            f"1{d}{s}f",
                        ]
                    )
                case "sub":
                    ram.extend(
                        [
                            # %f <- M[R[t]]
                            f"af0{t}",
                            # R[d] <- R[s] - %f
                            f"2{d}{s}f",
                        ]
                    )
            continue

        if m := expressions["op d s [lab]"].match(line):
            op = m.group("op")
            d = m.group("d")
            s = m.group("s")
            lab = m.group("lab")
            match op:
                case "and":
                    ram.extend(
                        [
                            # %f <- M[lab]
                            f"8f<{lab}>",
                            # R[d] <- R[s] & %f
                            f"3{d}{s}f",
                        ]
                    )
                case "or":
                    ram.extend(
                        [
                            # %f <- M[lab]
                            f"8f<{lab}>",
                            # %e <- R[s] & %f
                            f"3e{s}f",
                            # %d <- R[s] ^ %f
                            f"4d{s}f",
                            # R[d] <- %d ^ %e
                            f"4{d}de",
                        ]
                    )
                case "xor":
                    ram.extend(
                        [
                            # %f <- M[lab]
                            f"8f<{lab}>",
                            # R[d] <- R[s] ^ %f
                            f"4{d}{s}f",
                        ]
                    )
                case "lsh":
                    ram.extend(
                        [
                            # %f <- M[lab]
                            f"8f<{lab}>",
                            # R[d] <- R[s] << %f
                            f"5{d}{s}f",
                        ]
                    )
                case "rsh":
                    ram.extend(
                        [
                            # %f <- M[lab]
                            f"8f<{lab}>",
                            # R[d] <- R[s] >> %f
                            f"6{d}{s}f",
                        ]
                    )
                case "add":
                    ram.extend(
                        [
                            # %f <- M[lab]
                            f"8f<{lab}>",
                            # R[d] < R[s] + %f
                            f"1{d}{s}f",
                        ]
                    )
                case "sub":
                    ram.extend(
                        [
                            # %f <- M[lab]
                            f"8f<{lab}>",
                            # R[d] <- R[s] - %f
                            f"2{d}{s}f",
                        ]
                    )
            continue

        if m := expressions["op d s val"].match(line):
            op = m.group("op")
            d = m.group("d")
            s = m.group("s")
            val = m.group("val")
            match op:
                case "and":
                    ram.extend(
                        [
                            # %f <- val
                            *load("f", val),
                            # R[d] <- R[s] & %f
                            f"3{d}{s}f",
                        ]
                    )
                case "or":
                    ram.extend(
                        [
                            # %d <- val
                            *load("d", val),
                            # %f <- R[s] & %d
                            f"3f{s}d",
                            # %e <- R[s] ^ %d
                            f"4e{s}d",
                            # R[d] <- %e ^ %f
                            f"4{d}ef",
                        ]
                    )
                case "xor":
                    ram.extend(
                        [
                            # %f <- val
                            *load("f", val),
                            # R[d] <- R[s] ^ %f
                            f"4{d}{s}f",
                        ]
                    )
                case "lsh":
                    ram.extend(
                        [
                            # %f <- val
                            *load("f", val),
                            # R[d] <- R[s] << %f
                            f"5{d}{s}f",
                        ]
                    )
                case "rsh":
                    ram.extend(
                        [
                            # %f <- val
                            *load("f", val),
                            # R[d] <- R[s] >> %f
                            f"6{d}{s}f",
                        ]
                    )
                case "add":
                    ram.extend(
                        [
                            # %f <- val
                            *load("f", val),
                            # R[d] < R[s] + %f
                            f"1{d}{s}f",
                        ]
                    )
                case "sub":
                    ram.extend(
                        [
                            # %f <- val
                            *load("f", val),
                            # R[d] <- R[s] - %f]
                            f"2{d}{s}f",
                        ]
                    )
            continue

        raise ToyException(f"Bad line: '{line}'")

    if len(ram) > 256:
        raise ToyException(f"Memory overflow error: {len(ram)} lines.")

    for i in range(len(ram)):
        if m := SUBSTITUTION.search(ram[i]):
            lab = m.group("lab")
            if lab not in lookup_table:
                raise ToyException(f"Bad label: '{lab}'")
            ram[i] = (
                f"{ram[i][: m.start()]}"
                f"{hex(lookup_table[lab])[2:].rjust(2, '0')}"
                f"{ram[i][m.end() :]}"
            )

    machine_code = "\n".join(
        [
            f"PC: {get_pc()}",
            *[
                f"{hex(i)[2:].rjust(2, '0')}: {datum}"
                for i, datum in enumerate(ram)
            ],
        ]
    )

    return Assembled(assembly, lookup_table, machine_code)


def format_assembly(assembly: str) -> str: ...
