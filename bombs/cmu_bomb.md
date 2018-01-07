# CMU bomb
The bomb is in 6 different phases. 

There's a bit at the start of the binary which checks if an argument is set.
If it's called with exactly one argument, uses that as an input file.
If it's called with no argument, expects input from stdin.
Otherwise breaks.

## Phase 1
This is simple: it just compares the input to a fixed string.
The password is **Public speaking is very easy.**

## Phase 2
Reads in 6 integers, via the format string `%d %d %d %d %d %d`. Let's call them `x_1, ..., x_6`.
Checks that `x_1 = 1` - if not, explodes the bomb.

After that, the binary goes into a loop, checking that
`x_i = i*x_{i-1}`.
If this holds up until `x_6`, it succeeds, otherwise it explodes the bomb.

From this, we get the correct input as **1 2 6 24 120 720**.

## Phase 3
The program expects input in the form `%d %c %d`. Let's label these `x_1, x_2, x_3`.  These are placed on the stack at `[ebp - 0xc], [ebp - 0x5], [ebp - 0x4]` respectively.
After that, it checks if `x_1` is at most 7, and if so jumps to the value in memory at `0x80497e8 + 4*x_1`.

What's at these locations? Finding the code that will be executed when e.g. `x_1 = 0`:
```
[0x080489b0]> pv @ 0x80497e8
0x08048be0
[0x080489b0]> pdi 4 @ 0x08048be0
0x08048be0                 b371  mov bl, 0x71
0x08048be2       817dfc09030000  cmp dword [ebp - 4], 0x309
0x08048be9         0f84a0000000  je 0x8048c8f
0x08048bef           e808090000  call sym.explode_bomb
[0x080489b0]> pdi 3 @ 0x8048c8f
0x08048c8f               3a5dfb  cmp bl, byte [ebp - 5]
0x08048c92                 7405  je 0x8048c99
0x08048c94           e863080000  call sym.explode_bomb
```

So in this case, it will:
Check if `x_3 = 0x309`, otherwise explode.
Set BL to `0x71` and compare this to `x_2`. If equal, go to end of function, otherwise explode.

So we should be able to pass in valid input by setting these values (remembering that `x_2` has to be a character). This gives input of **0 q 777**, which works!
(Other solutions exist for different values of `x_1`.)

## Phase 4
Reads in an integer, and runs it through the function `func4`. Checks if the output is `0x37` - if so, succeeds, otherwise explodes.

Looking at the code, it's a recursive function, which satisfies the following definition:
```
f(0) = f(1) = 1
f(x) = f(x-1) + f(x-2) for x >= 2
```

So it's defining the Fibonacci numbers. `0x37 = 55` corresponds to `f(9)`, so **9** gives valid input.

## Phase 5
Takes in a string. Checks that the length is exactly 6 - if not, explodes.

It also loads a particular string from memory, named `array.123`.
It then loops over the input byte by byte, applying a particular transformation. It checks at the end if the result says *"giants"* - if so, succeeds, otherwise explodes.

The transformation itself does the following. (In this code chunk, EBX, ECX point to our input, ESI points to the string loaded from memory.)
```
[0x08048d2c]> pdi 5 @ 0x8048d57
0x08048d57               8a041a  mov al, byte [edx + ebx]
0x08048d5a                 240f  and al, 0xf
0x08048d5c               0fbec0  movsx eax, al
0x08048d5f               8a0430  mov al, byte [eax + esi]
0x08048d62               88040a  mov byte [edx + ecx], al
```

So for each byte `b` of our input, it replaces it with byte `b & 0xf` of `array.123`.
We need to pick input such that the result of this says *"giants"*.

The script `cmubomb_5.py` does this. One example that works is **O@EKMA**.

## Phase 6
This one is pretty long! We'll break up the code into different parts.
It starts off by reading 6 integers from the input. Let's label them `x_1, ..., x_6`. Loaded onto the stack from `[ebp - 0x18]`.

### Part 1
Loops through each `x_i`.
Checks that it's between 1 and 6 - if not, crashes.

Then loops through `x_{i+1}, ..., x_6`, and checks that none of them are equal to `x_i`. In other words, it's checking that they're all distinct.

So in summary: it checks that the input is the numbers 1,2,3,4,5,6 in some order.

### Part 2
This loop populates another 6 values on the stack, starting at `[ebp - 0x30]`. Let's call them `n_1, ..., n_6`.

It loops through 1 to 6. For each one:
Populate `n_i` with a variable called `node1`.
Loop for `x_i - 1` times, replacing `n_i` with `*(n_i + 8)`.

This structure suggests that there's some sort of graph structure or linked list existing in memory at node1, where the variable at position 8 points to the next node.

By looking at a memory dump, we'll assume this node type looks something like
```
struct Node {
  int data;
  int index;
  Node* next
}
```

(The second variable here is never actually used, but it's set to the index of the node in memory.)

So we have some sort of linked list in memory. This part puts the nodes of this list on the stack, in the order specified by our input.

### Part 3
This loop modifies the linked list structure. 
We go through the values in the order on the stack, setting `n_{i+1}.next = n_i`.

So we re-order the linked list in memory according to the order passed in.

### Part 4
This loop runs over the elements on the stack, and checks that
`n_{i+1}.data <= n_i.data`. If this isn't the case, it explodes. If it is, we finish the function.

### Solution
Now we understand what the binary is doing, the solution is easy: We want to pass in input such that the re-ordered list is in decreasing order.

By inspecting the data on the nodes (which we can do with `pxw`), we get the original data as
`0xfd, 0x2d5, 0x12d, 0x3e5, 0xd4, 0x1b0`.
So to put this in decreasing order, we want to input **4 2 6 3 1 5**.

## Secret phase!
There's a secret phase as well.

### Accessing secret phase
After each phase, the function `phase_defused` is called. If this is the 6th string we're reading, it displays the "Congratulations" message, and finishes the game.

However, before this it tries to read a particular bit of memory with the format string `%d %s`. If the string part says *austinpowers* then it goes onto the secret phase. 

Putting this through gdb, the bit of memory contained the string *"9"*. I guessed this was reading the solution to phase 4. Changing the solution for this phase to **9 austinpowers** lets us go onto the secret phase.

### Solving secret phase
Reads in an integer. Checks that it's between 1 and `0x3e9`. 
If so, runs `fun7`, with inputs the variable `n1` and the integer we input. We succeed if the output of the function is 7.

`fun7` is a recursive function. It takes in two inputs from the stack - we'll call them `p, x`.
It does the following:
- if `p = 0`, return -1
- compare `*p` and `x`:
    - if `*p = x`, return 0
    - if `*p > x`, return `2*f(*(p + 4), x)`
    - if `*p < x`, return `2*f(*(p + 8), x) + 1`
    
This makes us think of some sort of linked structure again, where `p` points to some memory containing some data and two pointers. Let's think of it as the following structure:
```
struct Tree {
  int data;
  Tree* left;
  Tree* right;
}
```

Looking in memory, this seems roughly correct. We have a binary tree with 15 nodes. It's balanced and in sorted order (so left.data <= data <= right.data).

Phrasing the function above in terms of the tree structure:
The function is doing a sort of search in the tree for `x`. Assuming it's in the tree, it returns a number in binary giving the path to `x`, where `0` is added for going left and `1` is added for going right.
(This function isn't unique e.g. the paths L and LL will both return 0.)

We want the function to return 7, which is 111 in binary, so one way to get this would be to go right three times. The node corresponding to RRR has data `0x3e9`, or**1001**. This solves the secret phase.
