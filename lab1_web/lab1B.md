# B grade
## Patching the binary
This binary was a little strange to start analysing.
Initially, it calls `signal` with signal 5. This is SIGTRAP, used by debuggers to add a breakpoint. The function attached does nothing.
`INT3` is then ran at various points in the code, which triggers SIGTRAP. This effectively acts as a `NOP`.

This messed up visual graph mode in radare2, because it didn't know to continue analysing code after the `INT3` instruction. I fixed this by manually patching the binary to change these to `NOP`. 
This is easy to do in radare2: Go into visual mode with `V @ main`, browse to the relevant lines, and press `A` to edit. After doing this, radare2 was able to display the whole function.

## Analysing it
Very similar structure to the C grade challenge:
There's a string S stored in memory, and it reads a password in from the user. It then loops through the characters in S, applies an operation to them, and checks it against a character of the password.

The operation this time is much more complicated, and it isn't immediately clear what effect it should do. Written out into pseudcode, it look like the following - the final value of EAX is what is checked against the input.
```
EBX = S[i]
EAX = ECX = i + 1
EDX = 0x66666667
(EDX, EAX) = EAX*EDX (EDX = high bytes, EAX = low bytes)
EDX >> 3
EAX = ECX
EAX >> 31
EDX -= EAX
EAX = EDX
EAX << 2
EAX += EDX
EAX << 2
EDX = ECX
EDX -= EAX
EAX = EDX
EAX ^= EBX
```

The code `lab1B.py` does this, and prints out the password. The valid password is **ju5T_w4Rm1ng_UP!**.

## Understanding the assembly
On XORing the password with S, we see that the valid password is just the string S XORed with the keystream 1,2,...,16. So the "encryption" here is very similar to the previous part.

Why does the above assembly do this? 
Lines 4 and 5 above are what's relevant. The password is only 16 bytes long, so the largest value of EAX at the start of the loop is 16. 
So the maximum possible value of EDX after line 4 is 6 (as `0x66666667 * 0x10` has upper 4 bytes equal to `0x6`), so after line 5 EDX is always 0.

Similarly, after line 7 EAX is always 0, because the upper 32th bit is always 0 (given the length of the password).
So after this line we have `(EAX, EBX, ECX, EDX) = (0, S[i], i+1, 0)`.

Tracing through the rest of the assembly, after the penultimate line we have
`(EAX, EBX, ECX, EDX) = (i+1, S[i], i+1, i+1)`.

So the final value of EAX is the string S XORed with `i+1`, giving the keystream above. (This would change if S were longer.)

I guess the moral is: it's very easy to write very obfuscated assembly!
