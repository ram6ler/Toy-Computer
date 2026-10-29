from .language import EXPRESSIONS, STRING_EXPRESSION
from .exception import ToyException


def keyword(k: str) -> str:
    return f'<span class="keyword">{k}</span>'


def format_assembly(assembly: str) -> str:

    result = list[str]()

    lines = [
        stripped for line in assembly.split("\n") if (stripped := line.strip())
    ]

    for line in lines:
        m = STRING_EXPRESSION.search(line)
        if m:
            line = f"{line[: m.start()]}<STRING>{line[m.end() :]}"
            string = m.group(0)
        else:
            string = ""

        if "//" in line:
            line, *rest = line.split("//")
            line = line.strip()
            comments = (
                f'<span class="comment">// {" // ".join(rest).strip()}</span>'
            )
        else:
            comments = ""

        if ":" in line:
            while ":" in line:
                label, *rest = line.split(":")
                result.append(
                    f'<div class="label_header">'
                    f'<span class="label">{label.strip()}</span>:'
                    "</div>"
                )
                line = ":".join(rest)

        line = line.strip().replace("<STRING>", string)

        if not line:
            if comments:
                result.append(f'<div class="sl_comment">{comments}</div>')
            continue

        if m := EXPRESSIONS[".main"].match(line):
            result.append(f'<span class="main">{line}</span> {comments}')
            continue

        if m := EXPRESSIONS[".input d"].match(line):
            d = m.group("d")
            result.append(
                f'<span class="special">.input</span> '
                f'<span class="register">%{d}</span> {comments}'
            )
            continue

        if m := EXPRESSIONS[".input [t]"].match(line):
            t = m.group("t")
            result.append(
                f'<span class="special">.input</span> '
                f'[<span class="register">%{d}</span>] {comments}'
            )
            continue

        if m := EXPRESSIONS[".input [lab]"].match(line):
            lab = m.group("lab")
            result.append(
                f'<span class="special">.input</span> '
                f'<span class="label">{lab}</span> {comments}'
            )
            continue

        if m := EXPRESSIONS[".input_u d"].match(line):
            d = m.group("d")
            result.append(
                f'<span class="special">.input_u</span> '
                f'<span class="register">%{d}</span> {comments}'
            )
            continue

        if m := EXPRESSIONS[".input_u [t]"].match(line):
            t = m.group("t")
            result.append(
                f'<span class="special">.input_u</span> '
                f'[<span class="register">%{t}</span>] {comments}'
            )
            continue

        if m := EXPRESSIONS[".input_u [lab]"].match(line):
            lab = m.group("lab")
            result.append(
                f'<span class="special">.input_u</span> '
                f'[<span class="label">{lab}</span>] {comments}'
            )
            continue

        if m := EXPRESSIONS[".input_str [d]"].match(line):
            d = m.group("d")
            result.append(
                f'<span class="special">.input_u</span> '
                f'[<span class="register">%{d}</span>] {comments}'
            )
            continue

        if m := EXPRESSIONS[".input_str [lab]"].match(line):
            lab = m.group("lab")
            result.append(
                f'<span class="special">.input_u</span> '
                f'[<span class="label">{lab}</span>] {comments}'
            )
            continue

        if m := EXPRESSIONS[".rand d"].match(line):
            d = m.group("d")
            result.append(
                f'<span class="special">.input_u</span> '
                f'<span class="register">%{d}</span> {comments}'
            )
            continue

        if m := EXPRESSIONS[".rand [t]"].match(line):
            t = m.group("t")
            result.append(
                f'<span class="special">.input_u</span> '
                f'[<span class="register">%{d}</span>] {comments}'
            )
            continue

        if m := EXPRESSIONS[".rand [lab]"].match(line):
            lab = m.group("lab")
            result.append(
                f'<span class="special">.input_u</span> '
                f'[<span class="label">{lab}</span>] {comments}'
            )
            continue

        if m := EXPRESSIONS["fmt d"].match(line):
            fmt = m.group("fmt")
            d = m.group("d")
            result.append(
                f'<span class="special">{fmt}</span> '
                f'<span class="register">%{d}</span> {comments}'
            )
            continue

        if m := EXPRESSIONS["fmt [t]"].match(line):
            fmt = m.group("fmt")
            t = m.group("t")
            result.append(
                f'<span class="special">{fmt}</span> '
                f'[<span class="register">%{t}</span>] {comments}'
            )
            continue

        if m := EXPRESSIONS["fmt [lab]"].match(line):
            fmt = m.group("fmt")
            lab = m.group("lab")
            result.append(
                f'<span class="special">{fmt}</span> '
                f'[<span class="label">{lab}</span>] {comments}'
            )
            continue

        if m := EXPRESSIONS[".line"].match(line):
            result.append('<span class="special">.line</span>')
            continue

        if m := EXPRESSIONS[".write [d]"].match(line):
            d = m.group("d")
            result.append(
                f'<span class="special">.write</span> '
                f'[<span class="register">%{d}</span>] {comments}'
            )
            continue

        if m := EXPRESSIONS[".write [lab]"].match(line):
            lab = m.group("lab")
            result.append(
                f'<span class="special">.write</span> '
                f'[<span class="label">{lab}</span>] {comments}'
            )
            continue

        if m := EXPRESSIONS["lab:"].match(line):
            lab = m.group("lab")
            result.append(f'<span class="label">{lab}</span>: {comments}')
            continue

        if m := EXPRESSIONS[".word"].match(line):
            result.append(f'<span class="special">.word</span> {comments}')
            continue

        if m := EXPRESSIONS[".data data"].match(line):
            data = m.group("data")
            values = [
                f'<span class="value">{datum.strip()}</span>'
                for datum in data.split(",")
            ]
            result.append(
                f'<span class="special">.data</span> {", ".join(values)} {comments}'
            )
            continue

        if m := EXPRESSIONS[".u_data data"].match(line):
            data = m.group("data")
            values = [
                f'<span class="value">{datum.strip()}</span>'
                for datum in data.split(",")
            ]
            result.append(
                f'<span class="special">.u_data</span> {", ".join(values)} {comments}'
            )
            continue

        if m := EXPRESSIONS[".stack val"].match(line):
            val = m.group("val")
            result.append(
                f'<span class="special">.stack</span> <span class="value">{val}</span> {comments}'
            )
            continue

        if m := EXPRESSIONS["push d lab"].match(line):
            d = m.group("d")
            lab = m.group("lab")
            result.append(
                f'<span class="keyword">push</span> '
                f'<span class="register">%{d}</span> '
                f'<span class="label">{lab}</span> '
                f"{comments}"
            )
            continue

        if m := EXPRESSIONS["pop d lab"].match(line):
            d = m.group("d")
            lab = m.group("lab")
            result.append(
                f'<span class="keyword">pop</span> '
                f'<span class="register">%{d}</span> '
                f'<span class="label">{lab}</span> '
                f"{comments}"
            )
            continue

        if m := EXPRESSIONS["len d lab"].match(line):
            d = m.group("d")
            lab = m.group("lab")
            result.append(
                f'<span class="keyword">len</span> '
                f'<span class="register">%{d}</span> '
                f'<span class="label">{lab}</span> '
                f"{comments}"
            )
            continue

        if m := EXPRESSIONS[".ascii ..."].match(line):
            string = m.group("string")

            result.append(
                f'<span class="special">.ascii</span> '
                f'<span class="string">"{string}"</span> '
                f"{comments}"
            )
            continue

        if m := EXPRESSIONS["halt"].match(line):
            result.append(f'<span class="keyword">halt</span> {comments}')
            continue

        if m := EXPRESSIONS["ld d [lab]"].match(line):
            d = m.group("d")
            lab = m.group("lab")
            result.append(
                f'<span class="keyword">ld</span> '
                f'<span class="register">%{d}</span> '
                f'<span class="label">{lab}</span> '
                f"{comments}"
            )
            continue

        if m := EXPRESSIONS["ld d [t]"].match(line):
            d = m.group("d")
            t = m.group("t")
            result.append(
                f'<span class="keyword">ld</span> '
                f'<span class="register">%{d}</span> '
                f'[<span class="register">%{t}</span>] '
                f"{comments}"
            )
            continue

        if m := EXPRESSIONS["st d [lab]"].match(line):
            d = m.group("d")
            lab = m.group("lab")
            result.append(
                f'<span class="keyword">st</span> '
                f'<span class="register">%{d}</span> '
                f'[<span class="label">{lab}</span>] '
                f"{comments}"
            )
            continue

        if m := EXPRESSIONS["st d [t]"].match(line):
            d = m.group("d")
            t = m.group("t")
            result.append(
                f'<span class="keyword">st</span> '
                f'<span class="register">%{d}</span> '
                f'[<span class="register">%{t}</span>] '
                f"{comments}"
            )
            continue

        if m := EXPRESSIONS["st val [lab]"].match(line):
            val = m.group("val")
            lab = m.group("lab")
            result.append(
                f'<span class="keyword">st</span> '
                f'<span class="value">{val}</span> '
                f'[<span class="label">{lab}</span>] '
                f"{comments}"
            )
            continue

        if m := EXPRESSIONS["st val [t]"].match(line):
            val = m.group("val")
            t = m.group("t")
            result.append(
                f'<span class="keyword">st</span> '
                f'<span class="value">{val}</span> '
                f'[<span class="register">%{t}</span>] '
                f"{comments}"
            )
            continue

        if m := EXPRESSIONS["jz d lab"].match(line):
            d = m.group("d")
            lab = m.group("lab")
            result.append(
                f'<span class="keyword">jz</span> '
                f'<span class="register">%{d}</span> '
                f'<span class="label">{lab}</span> '
                f"{comments}"
            )
            continue

        if m := EXPRESSIONS["jp d lab"].match(line):
            d = m.group("d")
            lab = m.group("lab")
            result.append(
                f'<span class="keyword">jp</span> '
                f'<span class="register">%{d}</span> '
                f'<span class="label">{lab}</span> '
                f"{comments}"
            )
            continue

        if m := EXPRESSIONS["jn d lab"].match(line):
            d = m.group("d")
            lab = m.group("lab")
            result.append(
                f'<span class="keyword">jn</span> '
                f'<span class="register">%{d}</span> '
                f'<span class="label">{lab}</span> '
                f"{comments}"
            )
            continue

        if m := EXPRESSIONS["je d s lab"].match(line):
            d = m.group("d")
            s = m.group("s")
            lab = m.group("lab")
            result.append(
                f'<span class="keyword">je</span> '
                f'<span class="register">%{d}</span> '
                f'<span class="register">%{s}</span> '
                f'<span class="label">{lab}</span> '
                f"{comments}"
            )

            continue

        if m := EXPRESSIONS["jmp lab"].match(line):
            lab = m.group("lab")
            result.append(
                f'<span class="keyword">jmp</span> '
                f'<span class="label">{lab}</span> '
                f"{comments}"
            )
            continue

        if m := EXPRESSIONS["call d lab"].match(line):
            d = m.group("d")
            lab = m.group("lab")
            result.append(
                f'<span class="keyword">call</span> '
                f'<span class="register">%{d}</span> '
                f'<span class="label">{lab}</span> '
                f"{comments}"
            )
            continue

        if m := EXPRESSIONS["ret d"].match(line):
            d = m.group("d")
            result.append(
                f'<span class="keyword">ret</span> '
                f'<span class="register">%{d}</span> '
                f"{comments}"
            )
            continue

        if m := EXPRESSIONS["mv d s"].match(line):
            d = m.group("d")
            s = m.group("s")
            result.append(
                f'<span class="keyword">mv</span> '
                f'<span class="register">%{d}</span> '
                f'<span class="register">%{s}</span> '
                f"{comments}"
            )
            continue

        if m := EXPRESSIONS["mv d lab"].match(line):
            d = m.group("d")
            lab = m.group("lab")
            result.append(
                f'<span class="keyword">mv</span> '
                f'<span class="register">%{d}</span> '
                f'<span class="label">{lab}</span> '
                f"{comments}"
            )
            continue

        if m := EXPRESSIONS["mv d val"].match(line):
            d = m.group("d")
            val = m.group("val")
            result.append(
                f'<span class="keyword">mv</span> '
                f'<span class="register">%{d}</span> '
                f'<span class="value">{val}</span> '
                f"{comments}"
            )

            continue

        if m := EXPRESSIONS["not d"].match(line):
            d = m.group("d")
            result.append(
                '<span class="keyword">not</span> '
                f'<span class="register">%{d}</span> '
                f"{comments}"
            )
            continue

        if m := EXPRESSIONS["op d s"].match(line):
            op = m.group("op")
            d = m.group("d")
            s = m.group("s")
            result.append(
                f'<span class="keyword">{op}</span> '
                f'<span class="register">%{d}</span> '
                f'<span class="register">%{s}</span> '
                f"{comments}"
            )
            continue

        if m := EXPRESSIONS["op d [t]"].match(line):
            op = m.group("op")
            d = m.group("d")
            t = m.group("t")
            result.append(
                f'<span class="keyword">{op}</span> '
                f'<span class="register">%{d}</span> '
                f'[<span class="register">%{t}</span>] '
                f"{comments}"
            )
            continue

        if m := EXPRESSIONS["op d [lab]"].match(line):
            op = m.group("op")
            d = m.group("d")
            lab = m.group("lab")
            result.append(
                f'<span class="keyword">{op}</span> '
                f'<span class="register">%{d}</span> '
                f'[<span class="label">{lab}</span>] '
                f"{comments}"
            )
            continue

        if m := EXPRESSIONS["op d val"].match(line):
            op = m.group("op")
            d = m.group("d")
            val = m.group("val")
            result.append(
                f'<span class="keyword">{op}</span> '
                f'<span class="register">%{d}</span> '
                f'<span class="value">{val}</span> '
                f"{comments}"
            )
            continue

        if m := EXPRESSIONS["op d s t"].match(line):
            op = m.group("op")
            d = m.group("d")
            s = m.group("s")
            t = m.group("t")
            result.append(
                f'<span class="keyword">{op}</span> '
                f'<span class="register">%{d}</span> '
                f'<span class="register">%{s}</span> '
                f'<span class="register">%{t}</span> '
                f"{comments}"
            )
            continue

        if m := EXPRESSIONS["op d s [t]"].match(line):
            op = m.group("op")
            d = m.group("d")
            s = m.group("s")
            t = m.group("t")
            result.append(
                f'<span class="keyword">{op}</span> '
                f'<span class="register">%{d}</span> '
                f'<span class="register">%{s}</span> '
                f'<span class="register">%{t}</span> '
                f"{comments}"
            )
            continue

        if m := EXPRESSIONS["op d s [lab]"].match(line):
            op = m.group("op")
            d = m.group("d")
            s = m.group("s")
            lab = m.group("lab")
            result.append(
                f'<span class="keyword">{op}</span> '
                f'<span class="register">%{d}</span> '
                f'<span class="register">%{s}</span> '
                f'[<span class="label">{lab}</span>] '
                f"{comments}"
            )
            continue

        if m := EXPRESSIONS["op d s val"].match(line):
            op = m.group("op")
            d = m.group("d")
            s = m.group("s")
            val = m.group("val")
            result.append(
                f'<span class="keyword">{op}</span> '
                f'<span class="register">%{d}</span> '
                f'<span class="register">%{s}</span> '
                f'<span class="value">{val}</span> '
                f"{comments}"
            )
            continue

        raise ToyException(f"Bad line: '{line}'")

    return (
        """
        <pre class="toy_computer">
            <style>
                .toy_computer {
                    font-size: 12pt;
                    font-family: 'IBM Plex Mono', monospace;
                }
                .toy_computer .label_header {
                    line-height: 0.4em;
                    font-weight: bold;
                }
                .toy_computer .line {
                    padding-left: 2em;
                    line-height: 0.4em;
                }
                .toy_computer .value {
                    color: black;
                }
            
                .toy_computer .string {
                    color: orangered;
                }

                .toy_computer .sl_comment {
                    line-height: 0.4em;
                }
            
                .toy_computer .comment {
                    color: gray;
                }
            
                .toy_computer .label {
                    color: green;
                }
            
                .toy_computer .keyword {
                    color: blue;
                    font-weight: bold;
                }
            
                .toy_computer .special {
                    color: blue;
                }
            
                .toy_computer .register {
                    color: darkviolet;
                }

                .toy_computer .main {
                    font-weight: bold;
                    padding: 0.2em;
                    background-color: lightgoldenrodyellow;
                }
            </style>
        """
        f"{'\n'.join(f'<div class="line">{line}</div>' if 'div' not in line else line for line in result)}"
        "</pre>"
    )
