"""
NPKmath Benchmark Engine
PART 1: Synthetic claim zoo capability coverage.
PART 2: Real-world claim calculations verification.
"""
import sys
import json
import random
import re
import math
import statistics
from decimal import Decimal, ROUND_HALF_UP, getcontext
import sympy as sp
import mpmath as mp

from npkmath.core import NPKCoreEngine
from npkmath.sieve import GoldenSieve

# Set baseline evaluation decimal precision
getcontext().prec = 90

FAMILIES = ["identity", "shortfall", "value", "bound", "dimensions"]
METHODS = ["Trust", "Lookup", "Float1", "Float5", "NKP-Math"]

def fib(n: int) -> int:
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

# ------------------------------------------------------------- Synthetic Generators
def _true_identity(rng):
    k = rng.randrange(9)
    a = rng.randint(2, 6)
    return [
        (f"sin({a}*x)**2+cos({a}*x)**2", "1"),
        (f"(x+{a})**3", f"x**3+{3*a}*x**2+{3*a*a}*x+{a**3}"),
        (f"x**2-{a*a}", f"(x-{a})*(x+{a})"),
        (f"cos({2*a}*x)", f"1-2*sin({a}*x)**2"),
        ("sin(x+y)", "sin(x)*cos(y)+cos(x)*sin(y)"),
        (f"exp({a}*x+y)", f"exp(x)**{a}*exp(y)"),
        (f"log(x**{a}*y)", f"{a}*log(x)+log(y)"),
        (f"x**{a}-1", "(x-1)*(" + "+".join(f"x**{j}" for j in range(a)) + ")"),
        (f"phi**{a+2}", f"{fib(a+2)}*phi+{fib(a+1)}"),
    ][k]

def _oracle_identity(L_str, R_str):
    sieve = GoldenSieve()
    r = random.Random(7)
    d = sieve.parse_expression(L_str) - sieve.parse_expression(R_str)
    syms = sorted(d.free_symbols, key=str)
    f = sp.lambdify(syms, d, modules="mpmath")
    with mp.workdps(80):
        try:
            for _ in range(24):
                pt = [mp.mpf(0.1) + mp.mpf(2.9) * mp.mpf(r.getrandbits(250)) / mp.mpf(2) ** 250 for _ in syms]
                if abs(f(*pt)) > mp.mpf(10) ** -60:
                    return False
        except Exception:
            return False
    return True

def gen_identity(rng):
    L, R = _true_identity(rng)
    dom = {"x": (0.1, 3.0), "y": (0.1, 3.0)} if "log" in L else None
    if rng.random()  1e-9 * max(1.0, abs(float(fl(*pt)))):
                    return False
            return True
        except Exception:
            return False
    if f == "value":
        try:
            return abs(float(sp.N(fparse(c["expr"]), 15)) - float(c["claimed"])) <= 1e-9
        except Exception:
            return False
    if f == "bound":
        try:
            fn = sp.lambdify(sp.Symbol("x"), fparse(c["expr"]), "numpy")
            import numpy as np
            xs = np.linspace(0, 10, 400 if npts > 1 else 50)
            return bool(np.max(np.abs(fn(xs))) > float(c["c"]))
        except Exception:
            return False
    return False

def decide(method, c, eng, rng):
    f = c["family"]
    if method == "Trust": return True
    if method == "Lookup":
        if f in ("identity", "shortfall"): return (c["L"], c["R"]) in _LOOKUP
        if f == "value": return (c["expr"], c["claimed"]) in _LOOKUP_VALUES
        if f == "dimensions": return c["eq"] in _LOOKUP_EQ
        return False
    if method == "Float1": return float_check(c, 1, rng)
    if method == "Float5": return float_check(c, 5, rng)
    
    # Target Production Framework Execution
    if f in ("identity", "shortfall"): return eng.identity(c["L"], c["R"], domain=c.get("domain"))["status"] in ["PROVED", "SUPPORTED", "CONDITIONAL"]
    if f == "value": return eng.value(c["expr"], c["claimed"])["status"] == "VERIFIED"
    if f == "bound": return eng.exceeds(c["expr"], "x", 0, 10, c["c"])["status"] == "PROVED"
    return eng.dimensions(c["eq"], _QD)["status"] == "CONSISTENT"

# ------------------------------------------------------------- Workflows
def run_seed(seed):
    claims = make_seed(seed)
    eng = NPKCoreEngine(precision=50)
    rng = random.Random(seed + 1)
    tally = {m: {fam: [0, 0, 0, 0] for fam in FAMILIES} for m in METHODS}
    for c in claims:
        for m in METHODS:
            d = decide(m, c, eng, rng)
            t = tally[m][c["family"]]
            t[0] += int(d == c["label"])
            t[1] += 1
            if not c["label"]:
                t[3] += 1
                t[2] += int(d)
    return tally

REAL = [
    ("identity", ("2*cos(pi/5)", "phi"), "accept", "screenshot:gemini-identity"),
    ("identity", ("phi", "1+1/phi"), "accept", "screenshot:gemini-identity"),
    ("identity", ("phi**2", "phi+1"), "accept", "doc:copilot-parameters"),
    ("identity", ("3*0.3333", "1"), "reject", "screenshot:triadic-flaw"),
    ("identity", ("0.3333+0.3333+0.3333", "0.9999"), "accept", "user:own-arithmetic"),
    ("identity", ("0.3333+0.3333+0.3333+0.0001", "1"), "accept", "user:own-arithmetic"),
    ("identity", ("1-3*(10**8-1)/(3*10**8)", "10**(-8)"), "accept", "screenshot:triadic-flaw"),
    ("value", ("2*pi/phi**2", "2.3999632297"), "accept", "doc:sieve-script"),
    ("value", ("3**9", "19683"), "accept", "screenshot:gemini-tictactoe"),
    ("exceeds", ("sin(x*pi)*phi**(x/10)/(pi*phi)", "x", 0, 10, "0.3333333333333333"), \"reject\", "doc:gate-script"),
    ("dimensions", ("Gmn = 8*pi*G/c**4*Tmn", {"Gmn": "L^-2", "G": "L^3 M^-1 T^-2", "c": "L T^-1", "Tmn": "M L^-1 T^-2"}), "accept", "gr-baseline"),
    ("dimensions", ("Gmn = 8*pi*G/c**4*(I*sqrt(X))**(1+b)*Tmn/sqrt(X)", {"Gmn": "L^-2", "G": "L^3 M^-1 T^-2", "c": "L T^-1", "Tmn": "M L^-1 T^-2", "X": "M L^-1 T^-2"}), "conditional", "screenshot:copilot-single-equation"),
]

def run_real():
    eng = NPKCoreEngine(precision=50)
    ok = 0
    print(f\"{'#':>2} {'source':<34}{'verdict':<13}{'expected':<12} status\")
    for i, (kind, args, exp, src) in enumerate(REAL, 1):
        v = getattr(eng, kind)(*args)
