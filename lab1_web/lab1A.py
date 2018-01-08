import sys

if len(sys.argv) != 2:
    print "Usage: python lab1A.py <name>"
    sys.exit(1)

name = sys.argv[1]

x = 0
for i, c in enumerate(name):
    x += ord(c)
    index = 0xffffffff if i == 0 else i-1 # unsigned decrement
    x ^= ord(name[index % len(name)])
    print x

print "Serial is %d" % x

