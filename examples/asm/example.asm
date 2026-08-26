t_prompt:           // Some useful strings
  .ascii "Input "
t_a:
  .ascii "A: "
t_b:
  .ascii "B: "
t_plus:
  .ascii " + "
t_equals:
  .ascii " = "

  .main             // Program start
  .write [t_prompt] // Output "Input "
  .write [t_a]      // Output "A: "
  .input %0         // Get signed value to %0
  .write [t_prompt] // Output "Input "
  .write [t_b]      // Output "B: "
  .input %1         // Get signed value to %1
  add %2 %0 %1      // Add values in %0 and %1; result in %2
  .den %0           // Output value in %0
  .write [t_plus]   // Output " + "
  .den %1           // Output value in %1
  .write [t_equals] // Output " = "
  .den %2           // Output value in %2
  .line             // Output new line
  halt              // End program