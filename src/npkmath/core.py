"""
NPKmath Sieve Engine
Handles string cleaning, expression parsing safely, and preliminary checks.
"""
import re
import sympy as sp


class GoldenSieve:
    def __init__(self):
        # Establish restricted mathematical globals for safe execution
        self._funcs = (
            "sin", "cos", "tan", "exp", "log", "sqrt", "Abs", "atan", "sinh",
            "cosh", "tanh"
        )
        self._globals = {
            k: getattr(sp, k)
            for k in ("Symbol", "Integer", "Float", "Rational", "Function", "Dummy") + self._funcs
        }
        self._globals["__builtins__"] = {}
        self._locals = {"phi": sp.GoldenRatio, "pi": sp.pi, "euler": sp.E}
        self._transforms = sp.parsing.sympy_parser.standard_transformations + (sp.parsing.sympy_parser.convert_xor,)
        self._unsafe_patterns = (
            r"__import__|eval\(|exec\(|open\(|input\(|globals\(|locals\(|getattr\(|setattr\(|delattr\(|lambda\s|import\s|from\s+\w+\s+import",
            r"os\.|sys\.|subprocess|pickle|ctypes|marshal|builtins|compile\(",
        )

    def parse_expression(self, s: str):
        """Converts raw string equations to exact SymPy objects. Decimals become exact Rationals."""
        if not s or len(s.strip()) == 0:
            raise ValueError("Empty mathematical expression string.")

        candidate = s.strip()
        if not self.pre_filter_claim(candidate):
            raise ValueError("Unsafe mathematical expression string.")

        # Ensure trailing or standalone decimals become true exact numeric ratios instead of float expansions
        candidate = re.sub(r"(?<![\w.])(\d+\.\d+)(?![\w.])", r"Rational('\1')", candidate)

        if not re.fullmatch(r"[A-Za-z0-9_+\-*/^%().,'\s]*", candidate):
            raise ValueError("Expression contains unsupported syntax.")

        return sp.parse_expr(
            candidate,
            local_dict=dict(self._locals),
            global_dict=dict(self._globals),
            transformations=self._transforms,
        )

    def pre_filter_claim(self, expression_str: str) -> bool:
        """Baseline sanity check for text strings."""
        if not expression_str or len(expression_str.strip()) == 0:
            return False

        stripped = expression_str.strip()
        for pattern in self._unsafe_patterns:
            if re.search(pattern, stripped, flags=re.IGNORECASE):
                return False
        return True
