# NPKmath

A modular, framework-agnostic Python library engineered for autonomous mathematical claim verification and self-improving evaluation loops.

## 🛠️ Architecture

- **Sieve Engine (`sieve.py`)**: A high-speed Golden-Ratio mod-3 pre-filter layer.
- **Core Verification (`core.py`)**: Symbolic evaluation powered by SymPy and arbitrary-precision calculations via mpmath.
- **Source Ledger (`ledger.py`)**: Dynamic state and reliability tracking utilizing a Bayesian Beta distribution model.
- **Autonomous Agent (`agent.py`)**: Closed-loop pipelines handling sequential multi-turn batch claims.

## 🚀 Quick Start

### Installation
Clone this repository and install it locally using your preferred packaging utility:
```bash
pip install .
```

### Running the Verification Pipeline
You can run the built-in batch validation playbook out of the box:
```bash
python examples/basic_verification.py
```

