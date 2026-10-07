"""
NPKmath Sieve Engine
Handles string cleaning, expression parsing safely, and preliminary checks.
"""
import re
import sympy as sp

class GoldenSieve:
    def __init__(self):
        # Establish restricted mathematical globals for safe execution
        self._funcs = ("sin", "cos", "tan", "exp", "log", "sqrt", "Abs", "atan", "sinh", "cosh", "tanh")
        self._globals = {k: getattr(sp, k) for k in ("Symbol", "Integer", "Float", "Rational", "Function", "Dummy") + self._funcs}
        self._globals["__builtins__"] = {}
        self._locals = {"phi": sp.GoldenRatio, "pi": sp.pi, "euler": sp.E}
        self._transforms = sp.parsing.sympy_parser.standard_transformations + (sp.parsing.sympy_parser.convert_xor,)

    def parse_expression(self, s: str):
        """Converts raw string equations to exact SymPy objects. Decimals become exact Rationals."""
        if not s or len(s.strip()) == 0:
            raise ValueError("Empty mathematical expression string.")
        # Ensure trailing or standalone decimals become true exact numeric ratios instead of float expansions
        s = re.sub(r"(?<![\w.])(\d+\.\d+)(?![\w.])", r"Rational('\1')", s)
        return sp.parse_expr(s, local_dict=dict(self._locals), global_dict=dict(self._globals), transformations=self._transforms)

    def pre_filter_claim(self, expression_str: str) -> bool:
        """Baseline sanity check for text strings."""
        return bool(expression_str and len(expression_str.strip()) > 0)
