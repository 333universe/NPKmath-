import pytest
import sympy as sp
from npkmath.sieve import GoldenSieve
from npkmath.theory import NumberTheoryEngine, KnowledgeClaim


def test_secure_sieve_integrated_ingestion():
    sieve = GoldenSieve()
    engine = NumberTheoryEngine(sieve=sieve)

    # Test valid primality expression string
    valid_claim = KnowledgeClaim(
        claim_id="tx-101",
        source_id="trusted_agent",
        property_type="primality",
        expression_str="2**13 - 1"  # 8191 (Mersenne prime)
    )

    is_valid, reliability = engine.ingest_new_knowledge(valid_claim)
    assert is_valid is True
    assert round(reliability, 4) == 0.6667

    # Verify it is stored as an exact SymPy Integer key
    expected_key = sp.Integer(8191)
    assert engine.verified_knowledge[expected_key]["primality"] is True

    # Test an invalid composite claim utilizing decimal expansion formatting
    invalid_claim = KnowledgeClaim(
        claim_id="tx-102",
        source_id="trusted_agent",
        property_type="primality",
        expression_str="9.0"  # Sieve converts this safely via Rational
    )

    is_valid_2, reliability_2 = engine.ingest_new_knowledge(invalid_claim)
    assert is_valid_2 is False
    assert reliability_2 == 0.5  # Alpha=2, Beta=2


def test_malicious_or_garbage_strings_fail_gracefully():
    sieve = GoldenSieve()
    engine = NumberTheoryEngine(sieve=sieve)

    broken_claim = KnowledgeClaim(
        claim_id="tx-103",
        source_id="untrusted_node",
        property_type="primality",
        expression_str="eval('import os')"  # Blocked by isolated global dictionary
    )

    is_valid, reliability = engine.ingest_new_knowledge(broken_claim)
    assert is_valid is False
    assert round(reliability, 4) == 0.3333  # Dropped immediately by error boundaries
