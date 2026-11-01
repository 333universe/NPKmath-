"""
NPKmath public API helpers.

These quick-access functions give a simpler front door to the library while
preserving the more flexible engine and agent classes for advanced usage.
"""

from typing import Any, Dict, Iterable, List, Optional

from .agent import NPKAutonomousAgent
from .core import NPKCoreEngine


def verify_identity(
    lhs: str,
    rhs: str,
    *,
    precision: int = 120,
    domain: Optional[Dict[str, tuple[float, float]]] = None,
) -> Dict[str, Any]:
    """Verify whether two symbolic expressions are equivalent."""
    engine = NPKCoreEngine(precision=precision)
    return engine.identity(lhs, rhs, domain=domain)


def verify_value(
    expression: str,
    claimed: Optional[str] = None,
    *,
    precision: int = 120,
) -> Dict[str, Any]:
    """Evaluate a numeric expression and optionally compare it to a claimed value."""
    engine = NPKCoreEngine(precision=precision)
    if claimed is None:
        return {
            "status": "VERIFIED",
            "detail": str(engine.evaluate_high_precision_numeric(expression)),
            "value": engine.evaluate_high_precision_numeric(expression),
        }
    return engine.value(expression, claimed)


def verify_matrix(
    matrix_a: List[List[str]],
    matrix_b: Optional[List[List[str]]] = None,
    *,
    operation: str = "rank",
    precision: int = 120,
) -> Dict[str, Any]:
    """Run a matrix validation operation with a small, friendlier API."""
    engine = NPKCoreEngine(precision=precision)
    return engine.matrix_verify(matrix_a, matrix_b or [], operation)


def run_batch_verification(
    claims: Iterable[Dict[str, Any]],
    *,
    precision: int = 120,
) -> List[Dict[str, Any]]:
    """Run a batch of claims through the autonomous verification pipeline."""
    agent = NPKAutonomousAgent(precision=precision)
    return agent.run_batch_pipeline(list(claims))


__all__ = [
    "NPKAutonomousAgent",
    "NPKCoreEngine",
    "verify_identity",
    "verify_value",
    "verify_matrix",
    "run_batch_verification",
]
