"""
NPKmath Test Suite: Core Engine
Verifies production mathematical verification endpoints.
"""
import pytest
from npkmath.core import NPKCoreEngine

def test_production_identity_proved():
    engine = NPKCoreEngine()
    # Verifies standard algebraic identity proved exactly
    res = engine.identity("sin(x)**2 + cos(x)**2", "1")
    assert res["status"] == "PROVED"

def test_production_identity_refuted():
    engine = NPKCoreEngine()
    # Verifies failing algebraic statement gets caught and refuted
    res = engine.identity("x + 1", "x + 2")
    assert res["status"] == "REFUTED"

def test_production_value_verification():
    engine = NPKCoreEngine()
    # Verifies decimal value approximation matching to decimal points
    res = engine.value("pi", "3.14159")
    assert res["status"] == "VERIFIED"

def test_production_exceeds_bounds():
    engine = NPKCoreEngine()
    # Verifies that interval checking refutes an impossible bound condition
    res = engine.exceeds("sin(x)", "x", 0, 1, "2.0")
    assert res["status"] == "REFUTED"
    
