import z3
import math

min = 1
max = 100000
points = [
    71947,
    21398,
    60212,
    14596,
    36555,
    62519,
    89360,
    49158,
    29345,
    177,
    # 59689
]

solver = z3.Solver()
state0, state1 = z3.BitVecs('state0 state1', 64)

def xs128p(state0, state1):
    s1 = state0
    s0 = state1
    s1 ^= s1 << 23
    s1 ^= z3.LShR(s1, 17)
    s1 ^= s0
    s1 ^= z3.LShR(s0, 26)

    return s0, s1

def to_double(random):
    return (random >> 11) / (1 << 53)

def normalize(val):
    return (val - min) / (max - min + 1)

def get_bounds(point):
    lo = normalize(point) * (1 << 53)
    hi = normalize(point + 1) * (1 << 53)
    return math.ceil(lo), math.ceil(hi) - 1

points = points[::-1]
for point in points:
    state0, state1 = xs128p(state0, state1)
    output = state0 + state1
    calc = z3.LShR(output, 11)

    lower, upper = get_bounds(point)
    solver.add(z3.And(lower <= calc, calc <= upper))


if solver.check() == z3.sat:
    model = solver.model()
    state = {}
    for d in model.decls():
        state[d.name()] = model[d]
    s0_val = state["state0"].as_long()
    s1_val = state["state1"].as_long()

    output = (s0_val + s1_val) & 0xFFFFFFFFFFFFFFFF
    next = math.floor(to_double(output) * (max - min + 1)) + min
    print(next)
else:
    print("failed")
