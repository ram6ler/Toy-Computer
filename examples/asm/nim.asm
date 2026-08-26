                // Some helpful strings.
t_welcome:      .ascii "Welcome to Nim!"
t_move_first:   .ascii "Move first? "
t_heaps:        .ascii "Heaps (2-6)? "
t_player:       .ascii "Your move."
t_which:        .ascii "Heap? "
t_count:        .ascii "Take? "
t_i_take:       .ascii "I take "
t_from_heap:    .ascii " from heap "
t_period:       .ascii "."
t_barrier:      .ascii "|"
t_pebble:       .ascii "o"
t_i:            .ascii "I "
t_you:          .ascii "You "
t_win:          .ascii "win!"

                // Space for the heaps of pebbles.
d_heaps:        .data 0, 0, 0, 0, 0, 0

                // Restrict heap sizes to 15.
c_mask:         .data 0x000f

                // Number of heaps.
v_no_heaps:     .word

                // Whether the player is up to move.
v_to_move:      .word

                // Draw heaps of pebbles.
show_heaps:     ld %0 [v_no_heaps]
                mv %1 d_heaps
                mv %2 0
draw_pebbles:   jz %0 done_show
                add %3 %1 %2
                ld %4 [%3]
                add %3 %2 1
                .den %3
                .write [t_barrier]
draw_pebble:    jz %4 done_pebble
                .write [t_pebble]
                sub %4 1
                jmp draw_pebble
done_pebble:    .line
                sub %0 1
                add %2 1
                jmp draw_pebbles
done_show:      .line
                ret %a

                // Check whether game is over.
check:          ld %0 [v_no_heaps]
                mv %1 d_heaps
                mv %2 0
                mv %3 0
loop_check:     jz %0 done_check
                add %4 %1 %2
                ld %5 [%4]
                add %3 %5
                add %2 1
                sub %0 1
                jmp loop_check
done_check:     jz %3 no_pebbles
                ret %a
no_pebbles:     jmp game_over

                // Choose computer's move.
computer:       ld %0 [v_no_heaps]
                mv %1 d_heaps
                mv %2 0
                mv %3 0
                // Find the nim sum.
xor_pebbles:    jz %0 done_xor
                add %4 %1 %2
                ld %5 [%4]
                xor %3 %5
                add %2 1
                sub %0 1
                jmp xor_pebbles
done_xor:       ld %0 [v_no_heaps]
                mv %2 0
                jz %3 bad_move
                // Find a good move.
find_move:      add %4 %1 %2
                ld %5 [%4]            
                xor %6 %5 %3          
                sub %7 %5 %6          
                jp %7 make_move
                add %2 1
                jmp find_move
                // No good moves exist; find a bad move.
                // (Just take one pebble from first heap with pebbles.)
bad_move:       add %4 %1 %2
                ld %5 [%4]
                jp %5 found_bad_move
                add %2 1
                jmp bad_move
found_bad_move: mv %7 1
                // Explain move and remove pebbles.
make_move:      mv %8 %4
                .write [t_i_take]
                .den %7
                .write [t_from_heap]
                add %8 %2 1
                .den %8
                .write [t_period]
                .line
                sub %5 %7
                st %5 [%4]
                ret %a

                // Get player's move.
player:         .write [t_player]
                .line
                mv %0 d_heaps  
                .write [t_which]
                .input %1
                sub %1 1
                add %2 %0 %1
                ld %3 [%2]
                .write [t_count]
                .input %4
                sub %5 %3 %4
                st %5 [%2]
                ret %a

                // Program start.
                .main
                .write [t_welcome]
                .line
                
                // Get whether player would like to go first.
                .write [t_move_first]
                mv %0 response
                .input_str [%0]
                ld %0 [%0]
                rsh %0 8
                mv %1 'y'
                xor %0 %1
                jz %0 player_first
                st 0 [v_to_move]
                jmp get_heaps
player_first:   st 1 [v_to_move]

                // Get the number of heaps to use.
get_heaps:      .write [t_heaps]
                .input %0
                and %0 [c_mask]
                st %0 [v_no_heaps]
                mv %1 d_heaps

                // Fill the heaps with a random number of pebbles.
random:         .rand %2
                and %2 [c_mask]
                st %2 [%1]
                sub %0 1
                jz %0 game_loop
                add %1 1
                jmp random 
                
                // Draw the heaps of pebbles.
game_loop:      call %a show_heaps
                // Check whether the game is over.
                call %a check 
                // Check whose move it is.
                ld %0 [v_to_move]
                jp %0 player_move

                // Get the computer's move.
                call %a computer
                // Set the next move to the player.
                st 1 [v_to_move]
                jmp game_loop

                // Get the player's move.
player_move:    call %a player
                // Set the next move to the computer.
                st 0 [v_to_move]
                jmp game_loop

                // Check who the winner is.
game_over:      ld %0 [v_to_move]
                jp %0 computer_wins

                // Player wins.
                .write [t_you]
                jmp end

                // Computer wins.
computer_wins:  .write [t_i]
end:            .write [t_win]
                .line
                halt

                // Reserve space for the string response.
response:       .word
