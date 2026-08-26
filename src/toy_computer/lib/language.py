from re import compile


START = r"^"
END = r"$"
SPACE = r"\s+"
OPEN = r"\["
CLOSE = r"\]"
MINUS = r"\-"
DOT = r"\."
DIGIT = r"[0-9a-fA-F]"
CHARACTER = r"'(?P<character>.)'"
INT_TYPE = r"(?:0b|0o|0x)"
OP2 = r"(?P<op>(?:and|or|xor|lsh|rsh|add|sub|not))"
OP3 = r"(?P<op>(?:and|or|xor|lsh|rsh|add|sub))"

LAB = r"(?P<lab>[a-z][a-z0-9_]*)"
VAL = f"(?P<val>(?:{MINUS}?{INT_TYPE}?{DIGIT}+)|(?:{CHARACTER}))"
DATA = r"(?P<data>.+)"
STRING = r'"(?P<string>.+)"'
D = f"%(?P<d>{DIGIT})"
S = f"%(?P<s>{DIGIT})"
T = f"%(?P<t>{DIGIT})"
AT_D = f"{OPEN}{D}{CLOSE}"
AT_T = f"{OPEN}{T}{CLOSE}"
AT_LAB = f"{OPEN}{LAB}{CLOSE}"
FMT = (
    "(?P<fmt>"
    f"{DOT}den|{DOT}u_den|"
    f"{DOT}bin|{DOT}u_bin|"
    f"{DOT}oct|{DOT}u_oct|"
    f"{DOT}hex|{DOT}u_hex|"
    f"{DOT}pattern|"
    f"{DOT}char"
    ")"
)

SUBSTITUTION = compile(f"<{LAB}>")
STRING_EXPRESSION = compile(STRING)
CHARACTER_EXPRESSION = compile(f"{START}{CHARACTER}{END}")


expressions = {
    # Main
    ".main": compile(f"{START}.main{END}"),
    # Input
    ".input d": compile(f"{START}.input{SPACE}{D}{END}"),
    ".input [t]": compile(f"{START}.input{SPACE}{AT_T}{END}"),
    ".input [lab]": compile(f"{START}.input{SPACE}{AT_LAB}{END}"),
    ".input_u d": compile(f"{START}.input_u{SPACE}{D}{END}"),
    ".input_u [t]": compile(f"{START}.input_u{SPACE}{AT_T}{END}"),
    ".input_u [lab]": compile(f"{START}.input_u{SPACE}{AT_LAB}{END}"),
    ".input_str [d]": compile(f"{START}.input_str{SPACE}{AT_D}{END}"),
    ".input_str [lab]": compile(f"{START}.input_str{SPACE}{AT_LAB}{END}"),
    ".rand d": compile(f"{START}.rand{SPACE}{D}{END}"),
    ".rand [t]": compile(f"{START}.rand{SPACE}{AT_T}{END}"),
    ".rand [lab]": compile(f"{START}.rand{SPACE}{AT_LAB}{END}"),
    # Output
    "fmt d": compile(f"{START}{FMT}{SPACE}{D}{END}"),
    "fmt [t]": compile(f"{START}{FMT}{SPACE}{AT_T}{END}"),
    "fmt [lab]": compile(f"{START}{FMT}{SPACE}{AT_LAB}{END}"),
    ".line": compile(f"{START}.line{END}"),
    ".write [d]": compile(f"{START}.write{SPACE}{AT_D}{END}"),
    ".write [lab]": compile(f"{START}.write{SPACE}{AT_LAB}{END}"),
    # Data
    ".word": compile(f"{START}.word{END}"),
    ".data data": compile(f"{START}.data{SPACE}{DATA}{END}"),
    ".u_data data": compile(f"{START}.u_data{SPACE}{DATA}{END}"),
    ".ascii ...": compile(f"{START}.ascii{SPACE}{STRING}{END}"),
    ".stack val": compile(f"{START}.stack{SPACE}{VAL}{END}"),
    "push d lab": compile(f"{START}push{SPACE}{D}{SPACE}{LAB}{END}"),
    "pop d lab": compile(f"{START}pop{SPACE}{D}{SPACE}{LAB}{END}"),
    "len d lab": compile(f"{START}len{SPACE}{D}{SPACE}{LAB}{END}"),
    # Labels
    "lab:": compile(f"{START}{LAB}:{END}"),
    "halt": compile(f"{START}halt{END}"),
    # Loads
    "ld d [lab]": compile(f"{START}ld{SPACE}{D}{SPACE}{AT_LAB}{END}"),
    "ld d [t]": compile(f"{START}ld{SPACE}{D}{SPACE}{AT_T}{END}"),
    # Stores
    "st d [lab]": compile(f"{START}st{SPACE}{D}{SPACE}{AT_LAB}{END}"),
    "st d [t]": compile(f"{START}st{SPACE}{D}{SPACE}{AT_T}{END}"),
    "st val [lab]": compile(f"{START}st{SPACE}{VAL}{SPACE}{AT_LAB}{END}"),
    "st val [t]": compile(f"{START}st{SPACE}{VAL}{SPACE}{AT_T}{END}"),
    # Jumps
    "jz d lab": compile(f"{START}jz{SPACE}{D}{SPACE}{LAB}{END}"),
    "jp d lab": compile(f"{START}jp{SPACE}{D}{SPACE}{LAB}{END}"),
    "jn d lab": compile(f"{START}jn{SPACE}{D}{SPACE}{LAB}{END}"),
    "je d s lab": compile(f"{START}je{SPACE}{D}{SPACE}{S}{SPACE}{LAB}{END}"),
    "jmp lab": compile(f"{START}jmp{SPACE}{LAB}{END}"),
    # Calls
    "call d lab": compile(f"{START}call{SPACE}{D}{SPACE}{LAB}{END}"),
    "ret d": compile(f"{START}ret{SPACE}{D}{END}"),
    # Moves
    "mv d s": compile(f"{START}mv{SPACE}{D}{SPACE}{S}{END}"),
    "mv d lab": compile(f"{START}mv{SPACE}{D}{SPACE}{LAB}{END}"),
    "mv d val": compile(f"{START}mv{SPACE}{D}{SPACE}{VAL}{END}"),
    # Operations
    "not d": compile(f"{START}not{SPACE}{D}{END}"),
    "op d s": compile(f"{START}{OP2}{SPACE}{D}{SPACE}{S}{END}"),
    "op d [t]": compile(f"{START}{OP2}{SPACE}{D}{SPACE}{AT_T}{END}"),
    "op d [lab]": compile(f"{START}{OP2}{SPACE}{D}{SPACE}{AT_LAB}{END}"),
    "op d val": compile(f"{START}{OP2}{SPACE}{D}{SPACE}{VAL}{END}"),
    "op d s t": compile(f"{START}{OP3}{SPACE}{D}{SPACE}{S}{SPACE}{T}{END}"),
    "op d s [t]": compile(
        f"{START}{OP3}{SPACE}{D}{SPACE}{S}{SPACE}{AT_T}{END}"
    ),
    "op d s [lab]": compile(
        f"{START}{OP3}{SPACE}{D}{SPACE}{S}{SPACE}{AT_LAB}{END}"
    ),
    "op d s val": compile(f"{START}{OP3}{SPACE}{D}{SPACE}{S}{SPACE}{VAL}{END}"),
}
