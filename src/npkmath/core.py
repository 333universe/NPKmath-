"""
NPKmath Core Engine
Executes mathematical verification using SymPy symbolic evaluation 
and Mpmath high-precision calculations.
"""
import sympy
import mpmath

from npkmath.sieve import GoldenSieve
from npkmath.ledger import SourceLedger

class NPKCoreEngine:
    def __init__(self, precision: int = 120):
        # Set high-precision arithmetic threshold
        mpmath.mp.dps = precision
        self.sieve = GoldenSieve()
        self.ledger = SourceLedger()

    def evaluate_symbolic_equality(self, expr1_str: str, expr2_str: str) -> bool:
        """Checks if two symbolic mathematical expressions are mathematically identical."""
        try:
            sym_expr1 = sympy.simplify(expr1_str)
            sym_expr2 = sympy.simplify(expr2_str)
            # Subtracting the expressions should result in zero if they match perfectly
            result = sympy.simplify(sym_expr1 - sym_expr2)
            is_equal = (result == 0)
            
            # Record result into state ledger
            self.ledger.record_verdict(is_equal)
            return is_equal
        except Exception:
            self.ledger.record_verdict(False)
            return False

        def evaluate_high_precision_numeric(self, expression_str: str) -> str:
        """Evaluates an explicit string expression down to high-precision digits."""
        try:
            value = sympy.N(sympy.sympify(expression_str), mpmath.mp.dps)
            return str(value)
        except Exception as e:
            raise ValueError(f"Failed numeric evaluation: {str(e)}")
            
