"""
NPKmath Test Suite: Core Engine
Verifies production mathematical verification endpoints.
"""
import pytest
from npkmath.core import NPKCoreEngine

def test_production_identity_proved():
    engine = NPKCoreEngine()
    res = engine.identity("sin(x)**2 + cos(x)**2", "1")
    assert res["status"] == "PROVED"

def test_production_identity_refuted():
    engine = NPKCoreEngine()
    res = engine.identity("x + 1", "x + 2")
    assert res["status"] == "REFUTED"

def test_production_value_verification():
    engine = NPKCoreEngine()
    res = engine.value("pi", "3.14159")
    assert res["status"] == "VERIFIED"

def test_production_exceeds_bounds():
    engine = NPKCoreEngine()
    res = engine.exceeds("sin(x)", "x", 0, 1, "2.0")
    assert res["status"] == "REFUTED"

def test_matrix_equality_proved():
    engine = NPKCoreEngine()
    mat_a = [["1", "x"], ["0", "1"]]
    mat_b = [["1", "x"], ["0", "1"]]
    res = engine.matrix_verify(mat_a, mat_b, "equality")
    assert res["status"] == "PROVED"

def test_matrix_invertible_proved():
    engine = NPKCoreEngine()
    mat = [["1", "0"], ["0", "1"]]
    res = engine.matrix_verify(mat, [], "invertible")
    assert res["status"] == "PROVED"

def test_matrix_rank_evaluation():
    engine = NPKCoreEngine()
    mat = [["1", "2"], ["2", "4"]]
    res = engine.matrix_verify(mat, [], "rank")
    assert res["status"] == "VERIFIED"
    assert "1" in res["detail"]
    
