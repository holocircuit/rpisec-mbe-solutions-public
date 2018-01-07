s = "isrveawhobpnutfg"

target = "giants"

print "".join(chr(0x40 + s.find(c)) for c in target)
