"""
NPKmath: A Self-Improving AI Knowledge & Mathematical Verification Engine.
"""

from .sieve import GoldenSieve
from .ledger import SourceLedger
from .core import NPKCoreEngine
from .agent import NPKAutonomousAgent

__version__ = "1.0.0"

# Explicitly define public namespace exports
__all__ = [
    "GoldenSieve",
    "SourceLedger",
    "NPKCoreEngine",
    "NPKAutonomousAgent",
]
