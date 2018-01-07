import struct

s = open("graph.out","rb").read()

def parse_u32(s):
    return struct.unpack("<L", s)[0]

def pointer_to_node_pos(p):
    START = 0x804c160
    return (p - START) / 12

def all_possible_paths(n):
    # all possible paths consisting of L, R, of length at most n
    yield ""
    if n == 0: return

    for path in all_possible_paths(n-1):
        yield "L" + path
        yield "R" + path

def output_for_path(nodes, path):
    active_node = nodes[0]
    value = active_node[1]

    for p in path:
        active_node = nodes[active_node[0 if p == "L" else 2]]
        value ^= active_node[1]

    return value

# Load nodes
nodes = []
for i in xrange(16):
    t = s[i*12:(i+1)*12]
    left = pointer_to_node_pos(parse_u32(t[:4]))
    data = parse_u32(t[4:8])
    right = pointer_to_node_pos(parse_u32(t[8:12]))

    nodes.append((left, data, right))

solution = 0x40475194
# Check all paths to find something matching solution
for path in all_possible_paths(16):
    if output_for_path(nodes, path) == solution:
        print path
