if __name__ == "__main__":
    from re import split
    from sys import argv

    from .lib.exception import ToyException
    from .lib.computer import Computer
    from .lib.assembler import assemble, format_assembly

    from prompt_toolkit import PromptSession
    from prompt_toolkit.completion import PathCompleter, NestedCompleter

    ComputerCompleter = NestedCompleter(
        {
            "load": PathCompleter(),
            "dump": PathCompleter(),
            "machine": PathCompleter(),
            "format": PathCompleter(),
            "run": None,
            "step": None,
            "erase": None,
            "clear": None,
            "quit": None,
            "help": None,
            "pc": None,
        },
        ignore_case=True,
    )

    session = PromptSession()

    def banner():
        print(
            r"""
            .-------..-------..--. .--.
            |       ||       ||  | |  |
            '-.   .-'|  .-.  ||  '-'  |
              |   |  |  | |  ||       |
              |   |  |  '-'  |'-.   .-'
              |   |  |       |  |   |
              '---'  '-------'  '---'
          """
        )
        print(
            """  Welcome to Toy Computer, a Python implementation of
  an imaginary computer described in chapter 6 of:

    Sedgewick, R. & Wayne, K. (2017)
    Computer Science: An Interdisciplinary Approach

  This implementation (and Toy Assembly) was created by
  Richard Ambler for use in computer science courses at
  Beijing World Youth Academy.

  No guarantees as to usability or correctness are
  made. Feel free to use or modify as needed.

  For further details, see:

    https://github.com/ram6ler/Toy-Computer
"""
        )

    def lineate(message: str) -> None:
        print(f" {message}".rjust(78, "."))

    def repl():
        banner()

        computer = Computer()

        def load_path(path: str) -> bool:
            try:
                with open(path) as f:
                    program = f.read()
            except FileNotFoundError:
                print(f"  File '{path}' not found...")
                return False
            except IsADirectoryError:
                print(f"  '{path}' is a directory...")
                return False

            try:
                if ".asm" in path:
                    assembled = assemble(program)
                    computer.load(assembled.machine_code)
                    print(f"  Compiled {path} as assembly.")
                    print(
                        "\n".join(
                            f"  {line}" for line in assembled.lookup_table.split("\n")
                        )
                    )
                    print(f"  PC: {hex(computer.pc)[2:].rjust(2, '0')}")
                else:
                    computer.load(program)
                    print(f"  Compiled {path} as machine language.")
                    print(f"  PC: {hex(computer.pc)[2:].rjust(2, '0')}")
                return True
            except ToyException as e:
                print("  * Error:")
                print(f"  {e.message}")
                return False

        def run_program():
            lineate("Run Started")
            try:
                computer.reset()
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
            instruction = session.prompt(
                "\n> ",
                completer=ComputerCompleter,
            )
            match split(r" +", instruction.strip()):
                case ["help"] | ["h"]:
                    print(
                        r"""
  To use:

  (h)elp              Display this help message.
    
  (l)oad [p]          Compile and load a machine language or
                      assembly language file p. (If .asm is
                      contained in the file name the language
                      is assumed to be assembly.) If no path is
                      provided, re-compile loaded file.
  
  (r)un               Run the program from the current position.
  
  (d)ump [p]          Output the memory and register data. If a path is
                      added, save dump to path p.
  
  (m)achine [p]       Output the current state as machine language. If
                      a path is added, save machine language to path p.
  
  (s)tep              Step through one fetch-decode-execute cycle.
  
  (c)lear             Reset computer to original loaded state.
  
  (e)rase             Clear registers and memory.
  
  (f)ormat [p]        Saves loaded assembly as formatted html to path p. 
  
  (q)uit              Quit.
  
  PC: {addr}          Set the program counter to address addr. (addr 
                      expected to be in hexadecimal.)
  
  {addr}: {val}       Write value val to one-byte memory address addr.
                      (Both addr and val are expected to be in hexadecimal.)
      """
                    )

                case ["load", path] | ["l", path]:
                    load_path(path)

                case ["clear"] | ["c"]:
                    computer.reset()
                    print("Cleared to original state.")

                case ["run"] | ["r"]:
                    run_program()

                case ["erase"] | ["e"]:
                    computer.clear()
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
                        with open(rest[0], "w") as f:
                            f.write(computer.dump)
                        print(f"  Dump written to {rest[0]}.")
                    else:
                        print(computer.dump)

                case ["machine", *rest] | ["m", *rest]:
                    if rest:
                        with open(rest[0], "w") as f:
                            f.write(computer.breakdown)
                        print(f"  State written to {rest[0]}.")
                    else:
                        print(
                            "\n".join(
                                f"  {line}" for line in computer.breakdown.split("\n")
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
                            print(f"  * Error\nFile '{load_path}' not found.")
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
                                computer.pc = a
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
                            print(f"  Value {hex(v)} cannot be stored in two bytes...")
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
                    print("  Not understood. Input 'help' for available instructions.")

    if len(argv) == 1:
        try:
            repl()
        except KeyboardInterrupt:
            print("\n  So long!\n")
    elif len(argv) == 2:
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
        print(
            """
  To use:
    python -m toy_computer
  or:
    python -m toy_computer [file]
  """
        )
