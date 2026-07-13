"Iteration and simple blocks"

Transcript showCr: 'Counting:'.
1 to: 5 do: [:i | Transcript showCr: i printString].

"A block that squares its argument"
| square name |
square := [:n | n * n].
Transcript showCr: 'Square of 7: ', (square value: 7) printString.

"Read a line from the console and greet it"
name := stdin nextLine.
Transcript showCr: 'Welcome, ', name, '!'.
