"""
NPKmath: A Self-Improving AI Knowledge & Mathematical Verification Engine.
"""

from .agent import NPKAutonomousAgent
from .api import (
    run_batch_verification,
    verify_identity,
    verify_matrix,
    verify_value,
)
from .core import NPKCoreEngine
from .ledger import SourceLedger
from .sieve import GoldenSieve
from .signals import AIFeedbackInterface, SignalRanker, VerificationSignal

__version__ = "1.0.0"

# Explicitly define public namespace exports
__all__ = [
    "NPKAutonomousAgent",
    "NPKCoreEngine",
    "SourceLedger",
    "GoldenSieve",
    "VerificationSignal",
    "AIFeedbackInterface",
    "SignalRanker",
    "verify_identity",
    "verify_value",
    "verify_matrix",
    "run_batch_verification",
]
