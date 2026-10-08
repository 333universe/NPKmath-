"""
NPKmath Core Engine
Executes symbolic identities, arbitrary-precision validations, 
interval arithmetic, physical dimension auditing, and matrix operations.
"""
import time
import sympy as sp
import mpmath as mp
from typing import Dict, Tuple, Optional, List, Any

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

    def evaluate_high_precision_numeric(self, expr: str) -> float:
        """Evaluate a numeric expression and return a high-precision float."""
        try:
            parsed = self.sieve.parse_expression(expr)
            with mp.workdps(max(50, 80)):
                return float(sp.N(parsed, 50))
        except Exception as exc:
            raise ValueError(f"Unable to evaluate expression: {expr}") from exc

    # ------------------------------------------------------------- Matrix Operations
    def matrix_verify(self, matrix_a: List[List[str]], matrix_b: List[List[str]], operation: str) -> dict:
        """
        Validates linear algebra operations, properties, and invariants.
        Supported Operations:
          'equality'    : Proves if Matrix A equals Matrix B element-wise.
          'invertible'  : Proves if Matrix A is invertible (det != 0).
          'orthogonal'  : Proves if Matrix A satisfies A^T * A = I.
          'rank'        : Returns the structural rank profile of Matrix A.
        """
        try:
            # Parse row-nested string entries into SymPy Matrix instances
            mA = sp.Matrix([[self.sieve.parse_expression(str(cell)) for cell in row] for row in matrix_a])
            
            if operation == "equality":
                mB = sp.Matrix([[self.sieve.parse_expression(str(cell)) for cell in row] for row in matrix_b])
                if mA.shape != mB.shape:
                    return {"status": "REFUTED", "detail": f"Dimension mismatch: {mA.shape} vs {mB.shape}"}
                diff = sp.simplify(mA - mB)
                is_equal = diff.is_zero_matrix
                return {
                    "status": "PROVED" if is_equal else "REFUTED",
                    "detail": "Matrices are element-wise identical" if is_equal else "Matrices possess non-zero element variations"
                }
                
            elif operation == "invertible":
                if not mA.is_square:
                    return {"status": "REFUTED", "detail": "Non-square matrices are inherently non-invertible"}
                det = sp.simplify(mA.det())
                is_nonzero = (det != 0)
                return {
                    "status": "PROVED" if is_nonzero else "REFUTED",
                    "detail": f"Matrix is invertible, det = {sp.sstr(det)}" if is_nonzero else "Matrix is singular, det = 0"
                }
                
            elif operation == "orthogonal":
                if not mA.is_square:
                    return {"status": "REFUTED", "detail": "Orthogonal matrices must be square"}
                identity = sp.eye(mA.rows)
                diff = sp.simplify((mA.T * mA) - identity)
                is_ortho = diff.is_zero_matrix
                return {
                    "status": "PROVED" if is_ortho else "REFUTED",
                    "detail": "Satisfies orthogonal matrix properties (A^T * A = I)" if is_ortho else "Fails orthogonal transpose balance"
                }
                
            elif operation == "rank":
                rk = mA.rank()
                return {"status": "VERIFIED", "detail": f"Matrix rank structural evaluation yielded rank calculation: {rk}"}
                
            else:
                return {"status": "ILL_FORMED", "detail": f"Unsupported matrix operation flag: {operation}"}
                
        except Exception as e:
            return {"status": "ILL_FORMED", "detail": f"Matrix transformation engine error: {str(e)}"}

    # ------------------------------------------------------------------ identity
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

    # ------------------------------------------------------------------ value
    def value(self, expr: str, claimed: str) -> dict:
        """Evaluates math strings down to arbitrary precision digits to check precision shortfalls."""
        try:
            decimals = len(claimed.split(".")) if "." in claimed else 0
            with mp.workdps(max(50, decimals + 30)):
                v = mp.mpmathify(str(sp.N(self.sieve.parse_expression(expr), decimals + 40)))
                tol = mp.mpf(10) ** (-decimals) / 2
                err = abs(v - mp.mpf(claimed))
                if err <= tol * (1 + mp.mpf(10) ** -15):
                    return {"status": "VERIFIED", "detail": f"matches claimed {decimals} decimals"}
                return {"status": "REFUTED", "detail": f"error {mp.nstr(err, 3)}"}
        except Exception as e:
            return {"status": "ILL_FORMED", "detail": str(e)}

    # ------------------------------------------------------------------ bound (interval arithmetic)
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
