"""
NPKmath Test Suite: Ledger Engine
Verifies Bayesian Beta distribution state updates and reliability tracking.
"""
from npkmath.ledger import SourceLedger

def test_ledger_initial_state():
    ledger = SourceLedger()
    summary = ledger.get_summary()
    assert summary["total_processed"] == 0
    # Baseline expected reliability for Beta(1,1) is exactly 0.5 (50.0%)
    assert summary["reliability_percentage"] == 50.0

def test_ledger_success_progression():
    ledger = SourceLedger()
    # Record a single true verdict
    ledger.record_verdict(True)
    summary = ledger.get_summary()
    assert summary["total_processed"] == 1
    # Beta(2,1) = 2 / (2 + 1) = 0.6666... -> 66.67%
    assert summary["reliability_percentage"] == 66.67

def test_ledger_failure_progression():
    ledger = SourceLedger()
    # Record a single false verdict
    ledger.record_verdict(False)
    summary = ledger.get_summary()
    assert summary["total_processed"] == 1
    # Beta(1,2) = 1 / (1 + 2) = 0.3333... -> 33.33%
    assert summary["reliability_percentage"] == 33.33
  
