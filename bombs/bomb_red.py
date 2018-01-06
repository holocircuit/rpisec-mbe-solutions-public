S = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"

def process(x, y, z):
    z = ((y << 27) & 0xffffffff) | (z >> 5)
    y = ((x << 27) & 0xffffffff) | (y >> 5)
    x = (x >> 5)
    return (x, y, z)

x = 0x6b8b4567
y = 0x327B23C6
z = 0x643C9869

s = ""
for i in xrange(19):
    s += S[z & 31]
    (x, y, z) = process(x, y, z)

print s
