"""
NPKmath Test Suite: Sieve Engine
Verifies string parsing and preliminary claim filtering.
"""
import pytest
import sympy as sp
from npkmath.sieve import GoldenSieve

def test_parse_expression_success():
    sieve = GoldenSieve()
    expr = sieve.parse_expression("x**2 + 1")
    assert expr is not None
    
    # Verifies that decimals are transformed into exact rational expressions
    expr_dec = sieve.parse_expression("0.3333")
    assert isinstance(expr_dec, sp.Rational)

def test_parse_expression_empty():
    sieve = GoldenSieve()
    with pytest.raises(ValueError):
        sieve.parse_expression("")

def test_pre_filter_claim_behavior():
    sieve = GoldenSieve()
    assert sieve.pre_filter_claim("x**2 + 1") is True
    assert sieve.pre_filter_claim("") is False
    assert sieve.pre_filter_claim("   ") is False
