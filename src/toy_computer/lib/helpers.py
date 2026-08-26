from .language import CHARACTER_EXPRESSION


def strip_hex(x: int, width=0) -> str:
    return hex(x)[2:].rjust(width, "0")


def parse_to_int(expression: str) -> int:
    if m := CHARACTER_EXPRESSION.match(expression.strip()):
        character = m.group("character")
        return ord(character) & 0xFF

    expression = expression.strip()
    f = 1
    if expression.startswith("-"):
        f = -1
        expression = expression[1:]

    if expression.startswith("0b"):
        result = f * int(expression[2:], base=2)
    elif expression.startswith("0o"):
        result = f * int(expression[2:], base=8)
    elif expression.startswith("0x"):
        result = f * int(expression[2:], base=16)
    else:
        result = f * int(expression)

    return result


def stdin_get_int() -> int:
    while True:
        try:
            response = parse_to_int(input())
            return response
        except ValueError:
            print("Bad input. Try again: ", end="")


def stdin_get_int_u() -> int:
    while True:
        try:
            response = parse_to_int(input())
            if response >= 0:
                return response
            print("Expecting an unsigned integer. Try again: ", end="")
        except ValueError:
            print("Bad input. Try again: ", end="")
