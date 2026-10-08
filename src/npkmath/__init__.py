"""
NPKmath: A Self-Improving AI Knowledge & Mathematical Verification Engine.
"""

from .agent import NPKAutonomousAgent
from .core import NPKCoreEngine
from .ledger import SourceLedger
from .sieve import GoldenSieve
from .signals import VerificationSignal, AIFeedbackInterface, SignalRanker

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
]

__all__ = ["NPKAutonomousAgent", "NPKCoreEngine", "SourceLedger", "GoldenSieve"]
