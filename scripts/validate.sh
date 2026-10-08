#!/usr/bin/env bash
# NPKmath Test Suite Runner
# Validates all core components and signal layer

set -e

echo "======================================"
echo "NPKmath Validation Suite"
echo "======================================"
echo ""

# Navigate to repo root
cd /path/to/NPKmath- || echo "Note: Update path to your repo root"

echo "[1/4] Installing package in editable mode with dev dependencies..."
python -m pip install -e ".[dev]" -q
echo "✓ Package installed"
echo ""

echo "[2/4] Running core engine tests..."
python -m pytest tests/test_core.py -v --tb=short
echo "✓ Core tests passed"
echo ""

echo "[3/4] Running signal module tests..."
python -m pytest tests/test_signals.py -v --tb=short
echo "✓ Signal tests passed"
echo ""

echo "[4/4] Validating package imports..."
python -c "
from npkmath import (
    NPKAutonomousAgent,
    NPKCoreEngine,
    SourceLedger,
    GoldenSieve,
    VerificationSignal,
    AIFeedbackInterface,
    SignalRanker,
)
print('✓ All imports successful')
print('✓ Package structure is clean')
"
echo ""

echo "======================================"
echo "Validation Complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "  1. Review test output above"
echo "  2. Integrate signals into agent.py"
echo "  3. Create ai_signal_export.py example"
echo "  4. Run end-to-end verification"
