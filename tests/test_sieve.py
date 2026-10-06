"""
NPKmath Test Suite: Sieve Engine
Verifies Golden-Ratio mod-3 filters and claim bounds.
"""
from npkmath.sieve import GoldenSieve

def test_verify_mod3_valid():
    sieve = GoldenSieve()
    # True because 3, 9, and 12 are completely divisible by 3
    assert sieve.verify_mod3(3) is True
    assert sieve.verify_mod3(9) is True
    assert sieve.verify_mod3(12) is True

def test_verify_mod3_invalid():
    sieve = GoldenSieve()
    # False because 1, 5, and non-integers fail mod-3 checks
    assert sieve.verify_mod3(1) is False
    assert sieve.verify_mod3(5) is False
    assert sieve.verify_mod3("string") is False

def test_pre_filter_claim_behavior():
    sieve = GoldenSieve()
    # Verifies string sanity controls
    assert sieve.pre_filter_claim("x**2 + 1") is True
    assert sieve.pre_filter_claim("") is False
    assert sieve.pre_filter_claim("   ") is False

