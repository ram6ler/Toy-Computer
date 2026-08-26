layers:
    .ascii ".---."  // 0
    .ascii "|   |"  // 1
    .ascii "|o  |"  // 2
    .ascii "|o o|"  // 3
    .ascii "|  o|"  // 4
    .ascii "| o |"  // 5
    .ascii "'---'"  // 6

d_offset:
    .data 0, 3, 6, 9, 12, 15

d_dice:
    .data 0, 0x0151, 0x0214, 0x0254, 0x0313, 0x0353, 0x0333

t_start:
    .ascii "Dice!"
t_how:
    .ascii "How many "
t_problems:
    .ascii "problems? "
t_problem:
    .ascii "Problem: "
t_dice:
    .ascii "dice? "
t_prompt:
    .ascii "Sum? "
t_correct:
    .ascii "Good!"
t_wrong:
    .ascii "Wrong!"  
t_score:
    .ascii "Score: "
t_slash:
    .ascii " / "

v_problems:
    .word
v_dice:
    .word
v_sum:
    .word

v_top:
    .word

draw_border:
    ld %0 [v_dice]
    mv %1 layers
    ld %2 [v_top]
    jp %2 border_loop
    add %1 18
border_loop: 
    jz %0 done_border
    .write [%1]
    sub %0 1
    jmp border_loop
done_border: 
    .line
    ret %b

draw_layer:
    ld %0 [v_dice]
    mv %1 layers


// throws the dice and stores the sum
throw:      
    ld %0 [v_dice]
    mv %1 dice_values
    mv %2 0
    mv %6 0
throw_loop:
    add %3 %1 %2
try_loop:   
    .rand %4
    and %4 0b111
    jz %4 try_loop
    sub %5 %4 6
    jp %5 try_loop
    st %4 [%3]
    add %6 %4
    add %2 1
    sub %0 1
    jz %0 done_try
    jmp throw_loop
done_try:
    st %6 [v_sum]
    ret %a

draw:
    mv %0 1
    st %0 [v_top]
    call %b draw_border
    ld %0 [v_dice]
    mv %0 dice_values
    mv %1 d_offset
    mv %2 d_dice
    mv %3 0xf000
    mv %4 12
next_layer:
    ld %5 [v_dice]
    sub %5 1
    rsh %3 4
    sub %4 4
layer_loop: 
    jn %5 done_layer
    add %6 %0 %5
    ld %6 [%6] // die value
    add %7 %2 %6
    ld %7 [%7] // layer indices
    and %7 %3
    rsh %7 %4 // layer index
    add %8 %1 %7
    ld %8 [%8] // offset
    mv %9 layers
    add %9 %8
    .write [%9]
    sub %5 1
    jmp layer_loop       
done_layer: 
    .line
    jz %4 done_layers
    jmp next_layer
done_layers:
    mv %0 0
    st %0 [v_top]
    call %b draw_border
    ret %a

v_problem_no:
    .word
v_correct:
    .word

    .main
    .write [t_start]
    .line
    .write [t_how]
    .write [t_problems]
    .input %0
    st %0 [v_problems]
    .write [t_how]
    .write [t_dice]
    .input %0
    st %0 [v_dice]
    mv %0 0
    st %0 [v_problem_no]
game_loop:
    ld %0 [v_problem_no]
    add %0 1
    .line
    .write [t_problem]
    .den %0
    .line
    call %a throw
    call %a draw
    .write [t_prompt]
    .input %1
    ld %2 [v_sum]
    je %1 %2 correct
    .write [t_wrong]
    jmp next_problem
correct:
    .write [t_correct]
    ld %0 [v_correct]
    add %0 1
    st %0 [v_correct]
next_problem:
    .line
    ld %0 [v_problem_no]
    ld %1 [v_problems]
    add %0 1
    je %0 %1 done
    st %0 [v_problem_no]
    jmp game_loop
done:
    .write [t_score]
    ld %0 [v_correct]
    .den %0
    .write [t_slash]
    ld %0 [v_problems]
    .den %0
    .line
    halt


dice_values:
    .word