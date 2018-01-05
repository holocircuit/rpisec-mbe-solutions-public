# RPISEC bomb
The binary displays a bomb, with 4 coloured wires. It asks you to choose a wire, and depending on what you use spawns a different function.

The aim is to "break" all of the wires. In the binary, these are variables called `wire_yellow`, etc for each colour. These start off set to *1* - we want to set them to *0*.

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

The jump at `0x0804999f` is not taken if `eax = 0`, i.e. if the value at `[ebp - 8]` is *0*. In this case `obj.wire_green` is divided by *2*, which sets it to 0! So we need to work out how to make sure this value is 0.

If we trace through, this value is initially set to *1*, and then is edited in the branch of code after checking it. Example code that edits it:

```
0x08049952               8b45f8  mov eax, dword [ebp - 8]
0x08049955               83e001  and eax, 1
0x08049958                 85c0  test eax, eax
0x0804995a               0f94c0  sete al
0x0804995d               0fb6c0  movzx eax, al
0x08049960               8945f8  mov dword [ebp - 8], eax
```

This reads `[ebp - 8]`, and sets it to *0* if it's odd, *1* if it's even. 
This is done twice, so it gets set back to *1* when it's checked at the end. If it started at any even value, it would end up as *0* and break the wire as we want.

### Cracking it
It turns out this program has a buffer overflow. Our input is read in at `[ebp - 0x14]`, and it reads up to `0x14` characters. 
(This can be seen by looking in the function `sym.green_preflight`).

The program only checks the first *8* characters, so we ca input characters after the password and it'll still be parsed as valid.
There's a stack protector (seen with the call to `__stack_chk_fail`), but we can overwrite the value at `[ebp - 0x8]` without breaking this.

We wanting this to have an even value, so the character *B* will do (ASCII code *0x42*). This needs to be at position `0x14 - 0x8 + 1 = 0xd` of our input. 
So e.g. **dcaotdaeXXXXB** works. Testing this, we break the green wire. :)

## Blue



