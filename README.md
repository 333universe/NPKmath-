# NPKmath

A modular, framework-agnostic Python library engineered for autonomous mathematical claim verification and self-improving evaluation loops.

## 🛠️ Architecture

- **Sieve Engine (`sieve.py`)**: A high-speed Golden-Ratio mod-3 pre-filter layer.
- **Core Verification (`core.py`)**: Symbolic evaluation powered by SymPy and arbitrary-precision calculations via mpmath.
- **Source Ledger (`ledger.py`)**: Dynamic state and reliability tracking utilizing a Bayesian Beta distribution model.
- **Autonomous Agent (`agent.py`)**: Closed-loop pipelines handling sequential multi-turn batch claims.
- **Signal Export (`signals.py`)**: Structured AI-readable verification signals and ranking utilities.

## 🚀 Quick Start

### Installation
Clone this repository and install it locally using your preferred packaging utility:

```bash
pip install .
```

### Public API
The package exposes a simple, documented public API for common tasks. Use the package-level convenience functions for fast integration, or drop down to `NPKCoreEngine` and `NPKAutonomousAgent` for more control.

```python
from npkmath import (
    verify_identity,
    verify_value,
    verify_matrix,
    run_batch_verification,
    NPKCoreEngine,
    NPKAutonomousAgent,
)

# Fast symbolic verification
result = verify_identity("(x + 1)^2", "x^2 + 2*x + 1")
print(result)

# High-precision numeric evaluation
numeric = verify_value("sin(pi/6)", claimed="0.5")
print(numeric)

# Matrix validation
matrix_result = verify_matrix(
    [["1", "0"], ["0", "1"]],
    operation="invertible",
)
print(matrix_result)

# Batch claim pipeline
claims = [
    {"id": "claim-1", "type": "numeric", "data": {"expression": "sqrt(16)", "claimed": "4"}},
    {"id": "claim-2", "type": "identity", "data": {"lhs": "(x + 1)^2", "rhs": "x^2 + 2*x + 1"}},
]
print(run_batch_verification(claims))

# Direct engine usage for advanced workflows
engine = NPKCoreEngine(precision=120)
print(engine.value("exp(0)", "1"))
```

### Running the Verification Pipeline
You can run the built-in batch validation playbook out of the box:

```bash
python examples/basic_verification.py
```

## API surface

The primary public entry points are:

- `verify_identity(lhs, rhs, *, precision=120, domain=None)`
- `verify_value(expression, claimed=None, *, precision=120)`
- `verify_matrix(matrix_a, matrix_b=None, *, operation="rank", precision=120)`
- `run_batch_verification(claims, *, precision=120)`
- `NPKCoreEngine` for direct symbolic/numeric/matrix verification logic
- `NPKAutonomousAgent` for autonomous claim-processing pipelines
- `AIFeedbackInterface` and `SignalRanker` for AI-consumable verification signals

This gives the library a clear, user-focused API while keeping the lower-level engine objects available when needed.
