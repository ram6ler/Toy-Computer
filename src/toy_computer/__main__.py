if __name__ == "__main__":
    from re import split
    from sys import argv

    from prompt_toolkit import PromptSession
    from prompt_toolkit.completion import NestedCompleter, PathCompleter

    from .lib.assembler import assemble
    from .lib.computer import Computer
    from .lib.exception import ToyException
    from .lib.format import format_assembly

    ComputerCompleter = NestedCompleter(
        {
            "load": PathCompleter(),
            "dump": PathCompleter(),
            "machine": PathCompleter(),
            "format": PathCompleter(),
            "build": PathCompleter(),
            "run": None,
            "step": None,
            "erase": None,
            "clear": None,
            "quit": None,
            "help": None,
            "instructions": None,
            "pc": None,
        },
        ignore_case=True,
    )

    session = PromptSession()

    def banner():
        print(
            r"""
                    ┌───────┐┌───────┐┌──┐ ┌──┐
                    │       ││       ││  │ │  │
                    └─┐   ┌─┘│  ┌─┐  ││  └─┘  │
                      │   │  │  │ │  ││       │
                      │   │  │  └─┘  │└─┐   ┌─┘
                      │   │  │       │  │   │
                      └───┘  └───────┘  └───┘
                   C   O   M   P   U   T   E   R
          """
        )
        print(
            """
  Welcome to Toy Computer, an implementation of an imaginary computer
  described in chapter 6 of:

    Sedgewick, R. & Wayne, K. (2017)
    Computer Science: An Interdisciplinary Approach

  This implementation and Toy Assembly were created by Richard Ambler
  for use in computer science courses at Beijing World Youth Academy.

  No guarantees as to usability or correctness are made. Feel free to
  use or modify as needed.

  For further details, see:

    https://github.com/ram6ler/Toy-Computer
"""
        )

    def show_help():
        print(
            r"""
  To use:

  help                Display this help message.

  instructions        Display instruction set.

  load p              Load a machine language or assembly language program from
                      file p. File p should have extension .asm if assembly, .mc
                      if machine language, or no extension if a compiled binary.

  build p             Compile current program to a binary file at path p.

  run                 Run the program from the current position.

  dump (p)            Output the memory and register data. If path p is given,
                      save dump to path p.

  machine (p)         Output the current state as machine language. If path p is
                      given, save machine language to path p.

  step                Step through one fetch-decode-execute cycle.

  clear               Reset computer to original loaded state.

  erase               Clear registers and memory.

  format p q          Saves assembly file at path p as formatted html at path d.

  PC: addr            Set the program counter to address addr, where addr is a
                      hexadecimal byte (two nibble digits).

  addr: val           Write value val to one-byte memory address addr, where addr
                      is a hexadecimal byte (two nibble digits) and val is a
                      hexadecimal word (four nibble digits).

  quit                Quit.
              """
        )

    def show_instructions():
        print("""
Instruction structure:
 ┌──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┐
 │  OPCODE   │     D     │     S     │     T     │
 └──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┘
 ┌──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┐
 │  OPCODE   │     D     │         ADDR          │
 └──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┘
Instructions:
 ┌────────┬─────────────────┬───────────────────────┐
 │ Opcode │ Description     │ Pseudocode            │
 ├────────┼─────────────────┼───────────────────────┤
 │ 0      │ Halt            │ Halt                  │
 │ 1      │ Add             │ R[D] ← R[S] + R[T]    │
 │ 2      │ Subtract        │ R[D] ← R[S] - R[T]    │
 │ 3      │ Bitwise And     │ R[D] ← R[S] & R[T]    │
 │ 4      │ Bitwise Xor     │ R[D] ← R[S] ^ R[T]    │
 │ 5      │ Left Shift      │ R[D] ← R[S] << R[T]   │
 │ 6      │ Right Shift     │ R[D] ← R[S] >> R[T]   │
 │ 7      │ Load Address    │ R[D] ← ADDR           │
 │ 8      │ Load            │ R[D] ← M[ADDR]        │
 │ 9      │ Store           │ M[ADDR] ← R[D]        │
 │ A      │ Load Indirect   │ R[D] ← M[R[T]]        │
 │ B      │ Store Indirect  │ M[R[T]] ← R[D]        │
 │ C      │ Branch Zero     │ if R[D] = 0 PC ← ADDR │
 │ D      │ Branch Positive │ if R[D] > 0 PC ← ADDR │
 │ E      │ Jump Register   │ PC ← R[D]             │
 │ F      │ Jump & Link     │ R[D] ← PC; PC ← ADDR  │
 └────────┴─────────────────┴───────────────────────┘
 Load Indirect (A) Extensions:
 ┌───┬─────────────────────────────────────┐
 │ S │ Description                         │
 ├───┼─────────────────────────────────────┤
 │ 0 │ Load Indirect (default)             │
 │ 1 │ R[D] ← signed integer from IO       │
 │ 2 │ R[D] ← unsigned integer from IO     │
 │ 3 │ M[R[D]..] ← condensed ASCII from IO │
 │ 4 │ R[D] ← random word                  │
 └───┴─────────────────────────────────────┘
 Store Indirect (B) Extensions:
 ┌───┬───────────────────────────────────────────┐
 │ S │ Description                               │
 ├───┼───────────────────────────────────────────┤
 │ 0 │ Store Indirect (default)                  │
 │ 1 │ Writes R[D] to IO as signed decimal       │
 │ 2 │ Writes R[D] to IO as unsigned decimal     │
 │ 3 │ Writes R[D] to IO as signed binary        │
 │ 4 │ Writes R[D] to IO as unsigned binary      │
 │ 5 │ Writes R[D] to IO as signed octal         │
 │ 6 │ Writes R[D] to IO as unsigned octal       │
 │ 7 │ Writes R[D] to IO as signed hexadecimal   │
 │ 8 │ Writes R[D] to IO as unsigned hexadecimal │
 │ 9 │ Writes R[D] to IO as binary pattern       │
 │ A │ Writes R[D] to IO as ASCII characters     │
 │ B │ Writes new line to IO                     │
 │ C │ Writes string starting at M[R[D]] to IO   │
 └───┴───────────────────────────────────────────┘
        """)

    def lineate(message: str) -> None:
        print(f" {message}".rjust(90, "."))

    def repl():
        banner()

        computer = Computer()

        def load_path(path: str) -> bool:
            if ".asm" in path or ".mc" in path:
                try:
                    with open(path) as f:
                        program = f.read()
                except FileNotFoundError:
                    print(f"  File '{path}' not found...")
                    return False
                except IsADirectoryError:
                    print(f"  '{path}' is a directory...")
                    return False
                except UnicodeDecodeError:
                    print("  * Error:")
                    print(f"  {path} is an invalid text file...")
                    return False

                try:
                    if ".asm" in path:
                        assembled = assemble(program)
                        computer.load(assembled.machine_code)
                        print(f"  Loaded {path} as assembly.")
                        print(
                            "\n".join(
                                f"  {line}"
                                for line in assembled.lookup_table.split("\n")
                            )
                        )
                        print(f"  PC: {hex(computer.pc)[2:].rjust(2, '0')}")

                    else:
                        computer.load(program)
                        print(f"  Loaded {path} as machine language.")
                        print(f"  PC: {hex(computer.pc)[2:].rjust(2, '0')}")
                    return True
                except ToyException as e:
                    print("  * Error:")
                    print(f"  {e.message}")
                    return False
            else:
                try:
                    t = Computer.from_binary(path)
                    computer.load(t.breakdown)
                    print(f"  Loaded {path} as compiled binary.")
                except ValueError:
                    print("  * Error:")
                    print("  Expecting a binary file.")
                    return False
                except ToyException as e:
                    print("  * Error:")
                    print(f"  {e.message}")
                    return False
            return True

        def run_program():
            lineate("Run Started")
            try:
                computer.clear()
                computer.run()
                print()
                lineate("Run Ended")
            except KeyboardInterrupt:
                print()
                lineate("Interrupted")
            except ToyException as e:
                print()
                print(f"  * Error\n  {e.message}")

        while True:
            try:
                instruction = session.prompt(
                    "\n> ",
                    completer=ComputerCompleter,
                )
            except EOFError:
                print("\n\n  So long!\n")
                exit()
            except KeyboardInterrupt:
                continue
            match split(r" +", instruction.strip()):
                case ["help"] | ["h"]:
                    show_help()

                case ["instructions"] | ["i"]:
                    show_instructions()

                case ["load", path] | ["l", path]:
                    load_path(path)

                case ["build", path] | ["b", path]:
                    try:
                        computer.save_as_binary(path)
                        print(f"Binary saved to {path}.")
                    except FileNotFoundError:
                        print(f"  File '{path}' not found...")
                    except IsADirectoryError:
                        print(f"  '{path}' is a directory...")
                    except PermissionError:
                        print(f"  Permission denied: '{path}'...")

                case ["clear"] | ["c"]:
                    computer.clear()
                    print("Cleared to original state.")

                case ["run"] | ["r"]:
                    run_program()

                case ["erase"] | ["e"]:
                    computer.erase()
                    print("All data erased.")

                case ["step"] | ["s"]:
                    print(
                        f"  PC: {hex(computer.pc)[2:].rjust(2, '0')} "
                        f"  CIR: {computer.ram[computer.pc]}"
                    )
                    lineate("Step Started")
                    try:
                        more_steps = computer.fetch_and_execute()
                        if not more_steps:
                            print()
                            lineate("Program complete")
                        else:
                            print()
                            lineate("Step Ended")

                    except ToyException as e:
                        print(f"  * Error: {e.message}")

                case ["dump", *rest] | ["d", *rest]:
                    if rest:
                        try:
                            with open(rest[0], "w") as f:
                                f.write(computer.dump)
                            print(f"  Dump written to {rest[0]}.")
                        except (
                            FileNotFoundError,
                            IsADirectoryError,
                            PermissionError,
                        ) as e:
                            print(f"  * Error: {e}")
                    else:
                        print(computer.dump)

                case ["machine", *rest] | ["m", *rest]:
                    if rest:
                        try:
                            with open(rest[0], "w") as f:
                                f.write(computer.breakdown)
                            print(f"  State written to {rest[0]}.")
                        except (
                            FileNotFoundError,
                            IsADirectoryError,
                            PermissionError,
                        ) as e:
                            print(f"  * Error: {e}")
                    else:
                        print(
                            "\n".join(
                                f"  {line}"
                                for line in computer.breakdown.split("\n")
                            )
                        )

                case ["format", path_src, path_dst] | ["f", path_src, path_dst]:
                    if ".asm" in path_src:
                        try:
                            with open(path_src) as f:
                                code = f.read()
                            with open(path_dst, "w") as f:
                                f.write(format_assembly(code))
                            print(f"  Written to {path_dst}.")
                        except FileNotFoundError:
                            print(f"  * Error\nFile '{path_src}' not found.")
                        except (IsADirectoryError, PermissionError) as e:
                            print(f"  * Error: {e}")
                    else:
                        print("  Expecting .asm in assembly file name...")

                case ["quit"] | ["q"]:
                    print("\n\n  So long!\n")
                    exit()

                case [sa, sv]:
                    if sa.lower() == "pc:":
                        try:
                            a = int(sv, 16)
                            if a < 0 or a > 0xFF:
                                print("  Expecting a one-byte value...")
                            else:
                                computer.reset_pc(a)
                                print(f"PC <- {hex(a)[2:].rjust(2, '0')}")
                        except ValueError:
                            print(
                                "  Not understood. "
                                "Input 'help' for available instructions."
                            )
                    else:
                        try:
                            a = int(sa.replace(":", ""), 16)
                        except ValueError:
                            print(
                                "  Not understood. "
                                "Input 'help' for available instructions."
                            )
                            continue
                        if a < 0 or a > 0xFF:
                            print("  Addresses range from 00 to ff...")
                            continue
                        try:
                            v = int(sv, 16)
                        except ValueError:
                            print(
                                "  Not understood. "
                                "Input 'help' for available instructions."
                            )
                            continue
                        if v < 0 or v > 0xFFFF:
                            print(
                                f"  Value {hex(v)} cannot be stored in two bytes..."
                            )
                            continue
                        print(
                            f"  M[{hex(a)[2:].rjust(2, '0')}] "
                            f"{computer.ram[a]} -> "
                            f"{hex(v)[2:].rjust(4, '0')}"
                        )
                        left_byte = (v & 0xFF00) >> 8
                        right_byte = v & 0xFF
                        computer.ram[a].update(bytes([left_byte, right_byte]))
                        print(
                            f"  ascii:      {computer.ram[a].characters}\n"
                            f"  value:      {computer.ram[a].value}\n"
                            f"  pseudocode: {computer.ram[a].pseudocode}"
                        )

                case _:
                    print(
                        "  Not understood. Input 'help' for available instructions."
                    )

    if len(argv) == 1:
        try:
            repl()
        except KeyboardInterrupt:
            print("\n  So long!\n")
    elif len(argv) == 2:
        if ".mc" in argv[1] or ".asm" in argv[1]:
            try:
                with open(argv[1]) as f:
                    code = f.read()
            except FileNotFoundError:
                print(f"  File '{argv[1]}' not found...")
                exit()

            computer = Computer()
            if ".asm" in argv[1]:
                assembled = assemble(code)
                computer.load(assembled.machine_code)
            else:
                computer.load(code)
            computer.run()
        else:
            computer = Computer.from_binary(argv[1])
            computer.run()
    else:
        print(
            """
  To use:
    python -m toy_computer
  or:
    python -m toy_computer [file]
  """
        )
