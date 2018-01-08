# A grade
The goal of this binary is a bit different to the others.
Rather than finding a password, the binary generates serial numbers for names. We want to understand the algorithm.

## Where is the code?
When we run the binary, we see a prompt for *"Serial:"*.
However, when we inspect the `main` function in radare2, we don't see this. 
If we search for the string and look for where it's referenced, we can see the code that prints this lives in `entry2.init`.
So there's "actual code" that's being done in the init functions, which are called before the main function.

## Patching the binary #1: removing anti-debugging
If we try and run the binary under gdb, we get a scary message saying *DEBUGGING IS A CRUTCH*.
This is being triggerd by code in `entry1.init`. It runs ptrace with all 0s, i.e.
`ptrace(PTRACE_TRACEME, 0, 0, 0)`

It checks if the result is -1 (i.e. an error) - if so it prints the message and exits.

ptrace is a system call used by gdb for attaching onto a process and inspecting it.
ptrace can't be called if a program is being traced. So the above check fails if run inside gdb, because ptrace has already been called.
So this is some sort of anti-debugging technique.

To remove this, we'll patch the binary, replacing the `JNE` instruction at `0x080486bd` with `JMP`.

## Patching the binary #2: being able to input a name
In `entry2.init`, we see a reference to a string *"Enter last name (5 or more characters)"*, but we didn't see that when running it.
The code is checking the length of a string in memory at `[ebp - 0x30]`. If it's 5 or more characters, it continues - if not it quits.

Inspecting the data here in gdb, it isn't zeroed out. So the program is passing this point with some random data on the stack.
We can patch the binary to make it accept our input instead. A simple way to do this is to just increase the size check to something like 12 characters instead. (There are null bytes further along the stack.)

## Analysing entry2.init
The binary potentially takes in a name, and saves it at `[ebp - 0x30]`. Let's call the input `S`.
It takes in a serial number, with format string `%d`, and saves it at address `0x804a034` in the .bss section.

After this, it does a loop that runs through each character of the input, and does some operations to the value at `0x804a038`. Let's call this `x`.

The loop of assembly is the following, where `[ebp - 0x34]` contains the current index:
```
[0x08048559]> pdi 27 @ 0x80485ef
0x080485ef               8d45d0  lea eax, [ebp - 0x30]
0x080485f2               0345cc  add eax, dword [ebp - 0x34]
0x080485f5               0fb600  movzx eax, byte [eax]
0x080485f8               0fbed0  movsx edx, al
0x080485fb           a138a00408  mov eax, dword [0x804a038]
0x08048600               8d3402  lea esi, [edx + eax]
0x08048603               8b45cc  mov eax, dword [ebp - 0x34]
0x08048606               83e801  sub eax, 1
0x08048609                 89c3  mov ebx, eax
0x0804860b               8d45d0  lea eax, [ebp - 0x30]
0x0804860e       c745c4ffffffff  mov dword [ebp - 0x3c], 0xffffffff
0x08048615                 89c2  mov edx, eax
0x08048617           b800000000  mov eax, 0
0x0804861c               8b4dc4  mov ecx, dword [ebp - 0x3c]
0x0804861f                 89d7  mov edi, edx
0x08048621                 f2ae  repne scasb al, byte es:[edi]
0x08048623                 89c8  mov eax, ecx
0x08048625                 f7d0  not eax
0x08048627               8d48ff  lea ecx, [eax - 1]
0x0804862a                 89d8  mov eax, ebx
0x0804862c           ba00000000  mov edx, 0
0x08048631                 f7f1  div ecx
0x08048633                 89d0  mov eax, edx
0x08048635           0fb64405d0  movzx eax, byte [ebp + eax - 0x30]
0x0804863a               0fbec0  movsx eax, al
0x0804863d                 31f0  xor eax, esi
0x0804863f           a338a00408  mov dword [0x804a038], eax
```

Translating this into pseudocode to try and understand what it does:
```
ESI = S[i] + x
EBX = i - 1
ECX = len(S)
EAX = EBX
EDX = EAX % ECX             # DIV divides ECX by EDX::EAX. Stores the quotient in EAX, modulus in EDX.
EAX = EDX = (i-1) % len(S)
EAX = S[EAX]
x = EAX ^ ESI
```

So this loops over each character of the string. It adds it to x, then XORs with a different byte of the string. 

The code in `lab1A.py` does this for any input string. It prints out each intermediate stage of the loop, along with the final value for the serial number. This also gives a concise description of the algorithm.

## Analysing main
Finally, we look at the main function itself. This is simple: it just checks that the end result of the calculation is equal to the serial number that was given. So the code above gives the correct serial number for any given name.


