| a b x |
a := 10.
b := 3.

Transcript showCr: 'Addition: ', (a + b) printString.
Transcript showCr: 'Subtraction: ', (a - b) printString.
Transcript showCr: 'Multiplication: ', (a * b) printString.
Transcript showCr: 'Integer division: ', (a // b) printString.
Transcript showCr: 'Float division: ', (a / b) asFloat printString.
Transcript showCr: 'Remainder: ', (a \\ b) printString.

"Shorthand-style update"
x := 5.
x := x + 2.
Transcript showCr: 'x after +2: ', x printString.
