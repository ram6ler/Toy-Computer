PC: 08;                                   (Set the PC to address 08)
00: 413a; "A:"                            (Some useful strings)
01: 2000; " "
02: 423a; "B:"
03: 2000; " "
04: 4120; "A "
05: 2b20; "+ "
06: 423a; "B:"
07: 2000; " "

; Program Start
08: 7000; R[0] <- 00
09: b0c0; stdout <- M[R[0]...]            (Output "A: ")
0a: a110; R[1] <- stdin (signed)          (Input a value to R[1])
0b: 7002; R[0] <- 02
0c: b0c0; stdout <- M[R[0]...]            (Output "B: ")
0d: a210; R[2] <- stdin (signed)          (Input a value to R[2])
0e: 1312; R[3] <- R[1] + R[2]             (Store the sum to R[3])
0f: 7004; R[0] <- 04
10: b0c0; stdout <- M[R[0]...]            (Output "A + B: ")
11: b310; stdout <- R[3] (signed denary)  (Output the value in R[3])
12: b0b0; stdout <- line                  (Output a new line)
13: 0000; halt