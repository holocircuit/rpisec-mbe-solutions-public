def process(i, c):
    ebx = ord(c)
    eax = i + 1
    ecx = i + 1
    edx = 0x66666667
    tmp = eax * edx
    eax = tmp & 0xffffffff
    edx = (tmp - eax) >> 32
    edx >>= 3
    eax = ecx
    eax >>= 31
    edx -= eax
    eax = edx
    eax << 2
    eax += edx
    eax <<= 2
    edx = ecx
    edx -= eax
    eax = edx
    eax ^= ebx
    return chr(eax)

s = "kw6PZq3Zd;ekR[_1"
print "".join(process(i, c) for i, c in enumerate(s))
