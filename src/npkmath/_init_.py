"""
NPKmath: A Self-Improving AI Knowledge & Mathematical Verification Engine.
"""

from npkmath.sieve import GoldenSieve
from npkmath.ledger import SourceLedger
from npkmath.core import NPKCoreEngine
from npkmath.agent import NPKAutonomousAgent

__version__ = "1.0.0"

# Explicitly define what is exposed when a user runs "from npkmath import *"
__all__ = [
    "GoldenSieve",
    "SourceLedger",
    "NPKCoreEngine",
    "NPKAutonomousAgent",
]
