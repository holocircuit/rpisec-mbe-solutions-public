# RPISEC bomb
The binary displays a bomb, with 4 coloured wires. It asks you to choose a wire, and depending on what you use spawns a different function.

The aim is to "break" all of the wires.

## Yellow
Can inspect this function in r2 by running `VV @ sym.yellow`.

Takes a password.
By inspecting the binary in radare2, we can see it checks the input byte by byte:
```
[0x08049719]> pdi 8 @ 0x0804972b
0x0804972b                 3c38  cmp al, 0x38
0x0804972d                 754d  jne 0x804977c
0x0804972f       0fb6054dc20408  movzx eax, byte [0x804c24d]
0x08049736                 3c34  cmp al, 0x34
0x08049738                 7542  jne 0x804977c
0x0804973a       0fb6054ec20408  movzx eax, byte [0x804c24e]
0x08049741                 3c33  cmp al, 0x33
0x08049743                 7537  jne 0x804977c
```

Looking at all of these lines and converting to ASCII, we get the password as **84371065**.

## Green






