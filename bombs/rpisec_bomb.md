# RPISEC bomb
The binary displays a bomb, with 4 coloured wires. It asks you to choose a wire, and depending on what you use spawns a different function.

The aim is to "break" all of the wires. In the binary, these are variables called `wire_yellow`, etc for each colour. These start off set to *1* - we want to set them to *0*. 
There's some logic at the start which I don't really understand. It spins off another thread, which periodically checks the wires. If any of them are *greater* than 1, it explodes.

I had some issues trying to run this in gdb, where it would crash immediately if I set any breakpoints. To get round this, I just stopped the other thread from starting (break at `0x0804950a` and jump over the call to `pthread_create`).

## Yellow
Can inspect this function in r2 by running `VV @ sym.yellow`.

Takes a password.
By inspecting the binary in radare2, we can see it checks the input byte by byte:
```
[0x08049719]> pdi 10 @ sym.yellow+11
0x08049724       0fb6054cc20408  movzx eax, byte [obj.buffer]
0x0804972b                 3c38  cmp al, 0x38
0x0804972d                 754d  jne 0x804977c
0x0804972f       0fb6054dc20408  movzx eax, byte [0x804c24d]
0x08049736                 3c34  cmp al, 0x34
0x08049738                 7542  jne 0x804977c
0x0804973a       0fb6054ec20408  movzx eax, byte [0x804c24e]
0x08049741                 3c33  cmp al, 0x33
0x08049743                 7537  jne 0x804977c
0x08049745       0fb6054fc20408  movzx eax, byte [0x804c24f]
```

Looking at all of the CMP lines and converting to ASCII, we get the password as **84371065**.

## Green
### Overview
Takes in input, and calls `strncmp`, comparing the first 8 bytes to a fixed string *dcaotdae*.
But if we try this, we see the adversary reset the wire, and nothing changes!

If we give the correct password, the only part of the code that changes `wire_green` is at the end of this function:

```
[0x08049904]> pdi 12 @ 0x804999a
0x0804999a               8b45f8  mov eax, dword [ebp - 8]
0x0804999d                 85c0  test eax, eax
0x0804999f                 750c  jne 0x80499ad
0x080499a1           a12cc10408  mov eax, dword [obj.wire_green]
0x080499a6                 d1f8  sar eax, 1
0x080499a8           a32cc10408  mov dword [obj.wire_green], eax
0x080499ad               8b45fc  mov eax, dword [ebp - 4]
0x080499b0       65330514000000  xor eax, dword gs:[0x14]
0x080499b7                 7405  je 0x80499be
0x080499b9           e8c6edffff  call sym.imp.__stack_chk_fail
0x080499be                   c9  leave
0x080499bf                   c3  ret
```

The jump at `0x0804999f` is not taken if `eax = 0`, i.e. if the value at `[ebp - 8]` is 0. In this case `obj.wire_green` is divided by 2, which sets it to 0! So we need to work out how to make sure this value is 0.

If we trace through, this value is initially set to 1, and then is edited in the branch of code after checking it. Example code that edits it:

```
0x08049952               8b45f8  mov eax, dword [ebp - 8]
0x08049955               83e001  and eax, 1
0x08049958                 85c0  test eax, eax
0x0804995a               0f94c0  sete al
0x0804995d               0fb6c0  movzx eax, al
0x08049960               8945f8  mov dword [ebp - 8], eax
```

This reads `[ebp - 8]`, and sets it to 0 if it's odd, 1 if it's even. 
This is done twice in this chunk of code, so it gets set back to 1 when it's checked at the end. If it started at any even value, it would end up as *0* and break the wire as we want.

### Cracking it
It turns out this program has a buffer overflow. Our input is read in at `[ebp - 0x14]`, and it reads up to `0x14` characters. 
(This can be seen by looking in the function `sym.green_preflight`).

The program only checks the first 8 characters, so we can input characters after the password and it'll still be parsed as valid.
There's a stack protector (seen with the call to `__stack_chk_fail`), but we can overwrite the value at `[ebp - 0x8]` without breaking this as long as we don't input too much.

We wanting this to have an even value, so the character *B* will do (ASCII code *0x42*). This needs to be at position `0x14 - 0x8 + 1 = 0xd` of our input. 
So e.g. **dcaotdaeXXXXB** works. Testing this, we break the green wire. :)

## Blue
Reads in up to 16 characters. For each one, compares to *'L'*, *'R'* or *'\n'* - blows up if it's not one of these. Each character of input changes some values on the stack.

After this, checks the value at `[ebp - 0x8]` to the value of the variable `solution`. If they're equal, breaks the blue wire, otherwise it blows up.

What does the program do with the input, and what are the values on the stack?
Before going into the loop, does the following:
```
0x080499fc       c745fc60c10408  mov dword [ebp - 4], obj.graph
0x08049a03               8b45fc  mov eax, dword [ebp - 4]
0x08049a06               8b4004  mov eax, dword [eax + 4]
0x08049a09               8945f8  mov dword [ebp - 8], eax
```

Code which is run on reading *'L'*, *'R'* respectively:
```
[0x08048810]> pdi 3 @ 0x8049a40
0x08049a40               8b45fc  mov eax, dword [ebp - 4]
0x08049a43                 8b00  mov eax, dword [eax]
0x08049a45               8945fc  mov dword [ebp - 4], eax
[0x08048810]> pdi 3 @ 0x8049a4a
0x08049a4a               8b45fc  mov eax, dword [ebp - 4]
0x08049a4d               8b4008  mov eax, dword [eax + 8]
0x08049a50               8945fc  mov dword [ebp - 4], eax
```

And then after each iteration of the loop, it runs the following:
```
[0x08048810]> pdi 3 @ 0x8049a77
0x08049a77               8b45fc  mov eax, dword [ebp - 4]
0x08049a7a               8b4004  mov eax, dword [eax + 4]
0x08049a7d               3145f8  xor dword [ebp - 8], eax
```

So it looks like `[ebp - 0x8]` contains some running XOR of values, 
and I guess `[ebp - 0x4]` maybe contains the current position in some graph?

If we look at the values in memory, it becomes clear. Example:
```
[0x080499f1]> px 12 @ obj.graph
- offset -   0 1  2 3  4 5  6 7  8 9  A B
0x0804c160  9cc1 0408 96fa bb47 78c1 0408
[0x080499f1]> px 12 @ 0x0804c19c
- offset -   0 1  2 3  4 5  6 7  8 9  A B
0x0804c19c  ccc1 0408 ef79 400c 14c2 0408
```

The words at position 0 and 8 look like pointers, which point to nearby locations of memory. 

This with the code above suggests the "graph" consists of nodes which look something like
```
struct Node{
  *Node left;
  int data;
  *Node right;
}
```

We start off with the data of the first node, stored at `obj.graph`.
*'L'* moves left, *'R'* moves right, and at each stage we XOR with the new data value. The aim is to finish with running total equal to `obj.solution`.

By looking at the hexdump manually, we can see there are 16 nodes in the graph, lying in continugous memory starting at `node1`. We can dump this out to a file by running `wtf graph.out 192 @ 0x0804c160`.

The script `bomb_blue.py` parses this, and brute forces to find a possible solution. 
**LLRR** is the shortest solution (many possibilities exist).

## Red
Unlike the others, the initial function that this runs (`sym.red_preflight`) is interesting. It generates 3 random numbers with a call to `rand()`, displays them and stores them in memory (at the variable named `r`).
The program never seeds the random number generator, so it always generates the same random numbers. (I'm not sure if this is a bug or not?)

It also loads a 32-byte string from memory, which is mostly equal to *[A-Z][0-9]*, with some characters removed.

After this, it loops through `0x13` bytes of input, checks it against the variables in memory, and then applies an operation to the 3 variables.

Unpicking what this does: Let's call the variables `x,y,z` in the order they're stored, and `S` the string.
The program checks that the byte of input is equal to `S[z & 31]`.

It then performs some assembly which in pseudocode does:
```
z = (y << 27) | (z >> 5)
y = (x << 27) | (y >> 5)
x = (x >> 5)
```

The script `bomb_red.py` runs through this logic, and prints out what the password should be.
For the random numbers my copy generated, this gave **KDG3DU32D38EVVXJM64**.
