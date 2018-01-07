S = "5tr0vZBrX:xTyR-P!"
print "".join(chr(ord(c) ^ i) for i,c in enumerate(S))
