# rpisec-mbe-solutions-public
Solutions to the reverse engineering challenges from RPISEC MBE.

My approach to these challenges:
I mainly used static analysis, using radare2 as an analyser. Visual graph mode (which you can get with `VV @ main`) is *extremely* helpful - it visually displays different blocks of assembly joined by jumps. Using this, it's pretty quick to understand the basic structure of the program.

Radare2 gives other useful commands for looking at the static variables of the program, e.g `pxw @ <pointer>` to print out words at a particular region.

I used gdb-peda as a debugger.

## What about the warzone exercises?
I'm also writing up solutions for the main warzone exercises, but am keeping these in a private repository. Let me know if you would like access.
