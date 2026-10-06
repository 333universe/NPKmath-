"""
NPKmath Test Suite: Core Engine
Verifies symbolic simplification and arbitrary-precision numeric calculations.
"""
import pytest
from npkmath.core import NPKCoreEngine

def test_symbolic_equality_success():
    engine = NPKCoreEngine()
    # Verifies algebraic identity expansions: (x-y)(x+y) equals x^2 - y^2
    assert engine.evaluate_symbolic_equality("x**2 - y**2", "(x - y)*(x + y)") is True
    # Verifies standard trigonometric identity: sin^2(x) + cos^2(x) equals 1
    assert engine.evaluate_symbolic_equality("sin(x)**2 + cos(x)**2", "1") is True

def test_symbolic_equality_failure():
    engine = NPKCoreEngine()
    # Unequal mathematical statements must return False instead of crashing
    assert engine.evaluate_symbolic_equality("x + 1", "x + 2") is False

def test_high_precision_numeric_evaluation():
    engine = NPKCoreEngine(precision=50)
    # Verifies that mpmath can evaluate expressions down to high-precision string decimals
    result = engine.evaluate_high_precision_numeric("sqrt(2)")
    # Check that it returned a valid string containing the high-precision decimal expansion of root 2
    assert isinstance(result, str)
    assert result.startswith("1.4142")
  
