
    intro_1: .ascii "I'm thinking of a number from 0 to 255."
    intro_2: .ascii "Try to guess it in the least number of guesses."
   guess_no: .ascii "Guess number: "
     prompt: .ascii "What is your guess? "
   too_high: .ascii "Too high! "
    too_low: .ascii "Too low! "
        try: .ascii "Try again!"
  correct_1: .ascii "Congratulations! You got it in "
  correct_2: .ascii " guesses!"
      again: .ascii "Play again (y/n)? "
        bye: .ascii "Bye!"
  
             .main
      start: .rand %0
             and %0 0xff         // %0 secret number
             .write [intro_1]
             .line
             .write [intro_2]
             .line
             mv %1 0             // %1 guesses
  
       loop: add %1 1
             .write [guess_no]
             .den %1
             .line
             .write [prompt]
             .input %2           // %2 guess
             je %0 %2 win
             sub %3 %0 %2
             jn %3 if_too_high
             .write [too_low]
             jmp end_loop

if_too_high: .write [too_high]

   end_loop: .write [try]
             .line
             jmp loop

       win: .write [correct_1]
            .den %1
            .write [correct_2]
            .line
            .write [again]
            mv %4 response
            .input_str [%4]
            ld %4 [%4]
            rsh %4 8
            xor %4 'y'
            jz %4 start
        
      done: .write [bye]
            .line
            halt

 response: .word
