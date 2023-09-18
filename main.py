import z3
import struct
import math

min = 1
max = 100000
points = [
    62351,
    68243,
    80445,
    60343,
    39020,
    4543,
    5524,
    82708,
    13099,
    29540
]

solver = z3.Solver()
state0, state1 = z3.BitVecs("state0 state1", 64)

def xs128p(state0, state1):
    s1 = state0
    s0 = state1
    s1 ^= s1 << 23
    s1 ^= z3.LShR(s1, 17)
    s1 ^= s0
    s1 ^= z3.LShR(s0, 26)

    return s0, s1

def to_double(state0):
    bits = (state0 >> 12) | 0x3FF0000000000000
    return struct.unpack('d', struct.pack('<Q', bits))[0] - 1

def from_double(val):
    return struct.unpack('<Q', struct.pack('d', val + 1))[0] & 0x3FFFFFFFFFFFFFFF

def normalize(val):
    return (val - min) / (max - min + 1)

points = points[::-1]
for point in points:
    state0, state1 = xs128p(state0, state1)
    calc = z3.LShR(state0, 12)

    lower = from_double(normalize(point))
    upper = from_double(normalize(point + 1))
    upper_exp = (upper >> 52) & 0x7FF
    lower = lower & 0x000FFFFFFFFFFFFF
    upper = upper & 0x000FFFFFFFFFFFFF

    solver.add(z3.And(lower <= calc, z3.Or(calc <= upper, upper_exp == 1024)))


if solver.check() == z3.sat:
    model = solver.model()
    state = {}
    for d in model.decls():
        state[d.name()] = model[d]
    state0 = state["state0"].as_long()
    state1 = state["state1"].as_long()

    next = math.floor(to_double(state0) * (max - min + 1)) + min
    print(next)
else:
    print("failed")
