    prompt: .ascii "What is your name? "
   pleased: .ascii "Pleased to meet you, "
   exclaim: .ascii "!"
    whoops: .ascii "Whoops! I guess I got it backwards!"
       ask: .ascii "Do you prefer it that way (y/n)? "
       yes: .ascii "I knew you would!"
        no: .ascii "Sorry to hear that!"
       bye: .ascii "Have a nice day!"

            .main
            .write [prompt]
            .input_str [space]
            mv %1 0

            // writes the number of characters to %1
     count: ld %2 [%0]
            and %3 %2 0xff00
            rsh %3 8
            jz %3 backwards
            add %1 1
            and %3 %2 0xff
            jz %3 backwards
            add %1 1
            add %0 1
            jmp count

 backwards: .write [pleased]
            mv %0 space

            // outputs the input string in reverse
      loop: and %2 %1 1 // offset (%1 mod 2)
            rsh %3 %1 1 // address (%1 div 2)
            add %4 %0 %3
            ld %5 [%4]
            mv %6 0xff
            jp %2 no_shift
            lsh %6 8
            and %7 %5 %6
            rsh %7 8
            jmp output

  no_shift: and %7 %5 %6
  
    output: .char %7
            sub %1 1
            jn %1 done_loop
            jmp loop

 done_loop: .write [exclaim]
            .line
            .write [whoops]
            .line
            .write [ask]
            .input_str [space]
            ld %1 [space]
            rsh %1 8
            xor %1 'y'
            jz %1 likes
            .write [no]
            jmp end

     likes: .write [yes]

       end: .line
            .write [bye]
            .line
            halt

     space: .word