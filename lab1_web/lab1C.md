# C grade
There's some string S in memory (a variable called `storedpass`). A pointer to this is loaded oto the stack at `[esp + 0x20]`. (This isn't the password though.)

The main code reads the password from the user, puts a pointer to it into `[esp + 0x28]`.

It then loops over each character of S, and does the following check. (In this code `[esp + 0x20]` starts at 0, and continues up to the length of S.)
```
[0x080484b4]> pdi 11 @ 0x80484ff
0x080484ff             8b442420  mov eax, dword [esp + 0x20]
0x08048503           0520a00408  add eax, str.5tr0vZBrX:xTyR_P
0x08048508               0fb610  movzx edx, byte [eax]
0x0804850b             8b442420  mov eax, dword [esp + 0x20]
0x0804850f                 31d0  xor eax, edx
0x08048511             88442427  mov byte [esp + 0x27], al
0x08048515             8d442428  lea eax, [esp + 0x28]
0x08048519             03442420  add eax, dword [esp + 0x20]
0x0804851d               0fb600  movzx eax, byte [eax]
0x08048520             3a442427  cmp al, byte [esp + 0x27]
0x08048524                 7413  je 0x8048539
```

If the jump is taken then we continue, if not then the password is rejected.
In words, this is comparing byte `i` of our input to the character `S[i] ^ i`.

The python code `lab1C.py` calculates what our input should be to match this. From this we get the correct password as **5up3r_DuP3r_u_#_1**.

## Sidenote on REPNE SCASB
The assembly used a pretty compact way of calculating the length of S, which I hadn't seen before.
The relevant code is
```
[0x080484b4]> pdi 10 @ 0x08048542
0x08048542           b820a00408  mov eax, str.5tr0vZBrX:xTyR_P
0x08048547     c744241cffffffff  mov dword [esp + 0x1c], 0xffffffff
0x0804854f                 89c2  mov edx, eax
0x08048551           b800000000  mov eax, 0
0x08048556             8b4c241c  mov ecx, dword [esp + 0x1c]
0x0804855a                 89d7  mov edi, edx
0x0804855c                 f2ae  repne scasb al, byte es:[edi]
0x0804855e                 89c8  mov eax, ecx
0x08048560                 f7d0  not eax
0x08048562               83e801  sub eax, 1
```

`REPNE SCASB` does the following (with AL, EDI as the operands):
Compare byte pointed to by EDI to AL.
If ECX = 0, continue to next line. Otherwise decrement ECX.
If equal, continue to next line.
Otherwise, increment EDI, stay at same line.

Here, ECX is initialised to -1, and EAX is 0.
If the string is length `n`, then after we exit this loop ECX will have value `-(n+2)`.

Then after the call to `NOT`, it will have value `n+1`.
And after subtracting 1, we get the length of the string.
