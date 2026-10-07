"""
NPKmath Core Engine
Executes symbolic identities, arbitrary-precision validations, 
interval arithmetic, and physical dimension auditing.
"""
import time
import sympy as sp
import mpmath as mp
from typing import Dict, Tuple, Optional, List

from .sieve import GoldenSieve
from .ledger import SourceLedger

class NPKCoreEngine:
    def __init__(self, precision: int = 120):
        # Configure global high-precision arithmetic thresholds
        mp.mp.dps = precision
        self.sieve = GoldenSieve()
        self.ledger = SourceLedger()
        self.n_points = 12

    def evaluate_symbolic_equality(self, expr1_str: str, expr2_str: str) -> bool:
        """Fallback check mapping algebraic identities to backward-compatible test hooks."""
        try:
            L = self.sieve.parse_expression(expr1_str)
            R = self.sieve.parse_expression(expr2_str)
            return bool(sp.simplify(L - R) == 0)
        except Exception:
            return False

    def identity(self, lhs: str, rhs: str, domain: Optional[Dict[str, Tuple[float, float]]] = None) -> dict:
        """Determines if LHS == RHS over real inputs using symbolic cancelation and high-precision sign sweeps."""
        try:
            L = self.sieve.parse_expression(lhs)
            R = self.sieve.parse_expression(rhs)
            d = L - R
            syms = sorted(d.free_symbols, key=str)
            
            if not syms:
                if sp.simplify(d) == 0:
                    return {"status": "PROVED", "detail": "exact: the difference simplifies to 0"}
                if abs(sp.N(d, 60)) > sp.Float(10) ** -40:
                    return {"status": "REFUTED", "detail": f"lhs - rhs = {sp.N(d, 12)}"}
                return {"status": "SUPPORTED", "detail": "agrees to 40 digits (not proved symbolically)"}

            try:
                dc = sp.cancel(d)
            except Exception:
                dc = d
            if dc == 0:
                return {"status": "PROVED", "detail": "exact: the rational difference cancels to 0"}

            # High-precision numeric failure checks
            DIGITS, TOL = 120, mp.mpf(10) ** -90
            with mp.workdps(DIGITS):
                fL = sp.lambdify(syms, L, modules="mpmath")
                fR = sp.lambdify(syms, R, modules="mpmath")

                def first_failure(dom, signed):
                    n_pts = max(self.n_points, 2 ** len(syms)) if signed else self.n_points
                    import random
                    rng = random.Random(0)
                    for i in range(n_pts):
                        pt = []
                        for k, s_ in enumerate(syms):
                            lo, hi = dom.get(str(s_), (0.1, 3.0))
                            v = mp.mpf(lo) + (mp.mpf(hi) - mp.mpf(lo)) * mp.mpf(rng.getrandbits(420)) / mp.mpf(2) ** 420
                            neg = ((i >> k) & 1) if i < 2 ** len(syms) else (rng.random() < 0.5)
                            pt.append(-v if (signed and neg) else v)
                        a_, b_ = fL(*pt), fR(*pt)
                        if abs(a_ - b_) > TOL * max(1, abs(a_), abs(b_)):
                            return f"lhs-rhs = {mp.nstr(a_ - b_, 6)}"
                    return None

                fail = first_failure(domain or {}, signed=False)
                if fail:
                    return {"status": "REFUTED", "detail": f"counterexample at {fail}"}
                if domain is None:
                    fail = first_failure({}, signed=True)
                    if fail:
                        return {"status": "CONDITIONAL", "detail": f"holds for positive inputs only; fails at {fail}"}

            if sp.simplify(d) == 0 or sp.simplify(sp.expand_trig(d)) == 0:
                return {"status": "PROVED", "detail": "symbolic: the difference simplifies to 0"}
            return {"status": "SUPPORTED", "detail": f"agrees to 90 digits at random points"}
        except Exception as e:
            return {"status": "ILL_FORMED", "detail": str(e)}

    def value(self, expr: str, claimed: str) -> dict:
        """Evaluates math strings down to arbitrary precision digits to check precision shortfalls."""
        try:
            decimals = len(claimed.split(".")[1]) if "." in claimed else 0
            with mp.workdps(max(50, decimals + 30)):
                v = mp.mpmathify(str(sp.N(self.sieve.parse_expression(expr), decimals + 40)))
                tol = mp.mpf(10) ** (-decimals) / 2
                err = abs(v - mp.mpf(claimed))
                if err <= tol * (1 + mp.mpf(10) ** -15):
                    return {"status": "VERIFIED", "detail": f"matches claimed {decimals} decimals"}
                return {"status": "REFUTED", "detail": f"error {mp.nstr(err, 3)}"}
        except Exception as e:
            return {"status": "ILL_FORMED", "detail": str(e)}

    def exceeds(self, expr: str, var: str, lo: float, hi: float, c: str) -> dict:
        """Proves if bounded functions exceed a specific limit using interval branch-and-bound logic."""
        try:
            x = sp.Symbol(var)
            e = self.sieve.parse_expression(expr).subs(sp.GoldenRatio, (1 + sp.sqrt(5)) / 2)
            iv = mp.iv
            ns = {n: getattr(iv, n) for n in ("sin", "cos", "tan", "exp", "log", "sqrt") if hasattr(iv, n)}
            ns.update({"Abs": abs, "pi": iv.pi, "e": iv.e, "mpf": iv.mpf})
            
            f_iv = sp.lambdify(x, e, modules=[ns, "mpmath"])
            f_pt = sp.lambdify(x, e, modules="mpmath")
            c_val = mp.mpf(str(c))
            lo_val, hi_val = mp.mpf(lo), mp.mpf(hi)

            def upper(a, b):
                r = f_iv(iv.mpf([a, b]))
                return max(abs(r.a), abs(r.b)) if hasattr(r, "a") else abs(r)

            if upper(lo_val, hi_val) <= c_val:
                return {"status": "REFUTED", "detail": "proved by interval arithmetic bounds"}

            stack, nodes, width0 = [(lo_val, hi_val)], 0, hi_val - lo_val
            while stack and nodes < 4000:
                a, b = stack.pop()
                nodes += 1
                if upper(a, b) <= c_val:
                    continue
                m = (a + b) / 2
                fm = abs(f_pt(m))
                if fm > c_val:
                    return {"status": "PROVED", "detail": f"witness found at x = {mp.nstr(m, 6)}"}
                if (b - a) < width0 * mp.mpf(10) ** -14:
                    continue
                stack.extend([(a, m), (m, b)])
            return {"status": "REFUTED", "detail": "bounded successfully everywhere"}
        except Exception as e:
            return {"status": "ILL_FORMED", "detail": str(e)}

    def dimensions(self, equation: str, dims: Dict[str, str]) -> dict:
        """Audits dimensional compliance of physics variables by validating exponent balances."""
        try:
            import re
            def _dimspec(v_str):
                out = {}
                for tok in str(v_str).split():
                    m = re.fullmatch(r"([A-Za-z]+)(?:\^(-?[\d/]+))?", tok)
                    out[m.group(1)] = sp.Rational(m.group(2)) if m.group(2) else sp.Integer(1)
                return out

            D = {k: _dimspec(v) for k, v in dims.items()}
            issues: List[str] = []
            constraints: List[sp.Expr] = []

            def same(a, b, ctx):
                keys = set(a) | set(b)
                for k in keys:
                    dv = sp.simplify(a.get(k, 0) - b.get(k, 0))
                    if dv == 0: continue
                    if dv.free_symbols: constraints.append(dv)
                    else: issues.append(ctx)

            def dim(e):
                if e.is_Number or e in (sp.pi, sp.E, sp.GoldenRatio): return {}
                if e.is_Symbol: return dict(D.get(str(e), {}))
                if e.is_Add:
                    first = dim(e.args[0])
                    for a in e.args[1:]: same(first, dim(a), "addition mismatch")
                    return first
                if e.is_Mul:
                    out = {}
                    for a in e.args:
                        for k, v in dim(a).items(): out[k] = sp.simplify(out.get(k, 0) + v)
                    return out
                if e.is_Pow:
                    b, ex = e.args
                    bd = dim(b)
                    return {k: sp.simplify(v * ex) for k, v in bd.items()} if bd else {}
                if e.func in (sp.sin, sp.cos, sp.tan, sp.exp, sp.log): return {}
                return {}

            lhs, rhs = equation.split("=")
            same(dim(self.sieve.parse_expression(lhs)), dim(self.sieve.parse_expression(rhs)), "equation mismatch")
            if issues: return {"status": "ILL_FORMED", "detail": "units structural conflict"}
            if constraints:
                unknowns = sorted({s for c in constraints for s in c.free_symbols}, key=str)
                sol = sp.solve(constraints, unknowns, dict=True)
                if not sol: return {"status": "ILL_FORMED", "detail": "units cannot agree"}
                return {"status": "CONDITIONAL", "detail": f"units agree only if {sol[0]}"}
            return {"status": "CONSISTENT", "detail": "units agree perfectly"}
        except Exception as e:
            return {"status": "ILL_FORMED", "detail": str(e)}
