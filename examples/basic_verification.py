"""
NPKmath Agent Engine
Handles autonomous multi-turn evaluation loops and runtime verification cycles.
"""
import time
from typing import Dict, List, Any

from npkmath.core import NPKCoreEngine


class NPKAutonomousAgent:
    def __init__(self, precision: int = 120):
        # Instantiate the main evaluation layer (which includes the sieve and ledger)
        self.engine = NPKCoreEngine(precision=precision)
        self.execution_history: List[Dict[str, Any]] = []

    def process_claim_cycle(self, claim_id: str, claim_type: str, data: Dict[str, str]) -> Dict[str, Any]:
        """
        Runs an autonomous evaluation loop iteration on an incoming claim packet.
        Supported claim types:
          - symbolic / identity: requires expr1 and expr2 or lhs and rhs
          - numeric / value: requires expression and optionally claimed
          - matrix: requires matrix_a, matrix_b, operation
        """
        start_time = time.perf_counter()
        verdict = "REFUTED"
        detail = None

        try:
            if claim_type in {"symbolic", "identity"}:
                expr1 = data.get("expr1") or data.get("lhs", "")
                expr2 = data.get("expr2") or data.get("rhs", "")

                if not expr1 or not expr2:
                    verdict = "UNKNOWN_CLAIM_TYPE"
                    self.engine.ledger.record_verdict(False)
                elif self.engine.sieve.pre_filter_claim(expr1) and self.engine.sieve.pre_filter_claim(expr2):
                    is_valid = self.engine.evaluate_symbolic_equality(expr1, expr2)
                    verdict = "PROVED" if is_valid else "REFUTED"
                    detail = f"symbolic equality check for {expr1} == {expr2}"
                    self.engine.ledger.record_verdict(is_valid)
                else:
                    verdict = "REJECTED_BY_SIEVE"
                    detail = "symbolic claim failed the sieve pre-filter"
                    self.engine.ledger.record_verdict(False)

            elif claim_type in {"numeric", "value"}:
                expression = data.get("expression") or data.get("expr", "")
                claimed = data.get("claimed")

                if not expression:
                    verdict = "UNKNOWN_CLAIM_TYPE"
                    self.engine.ledger.record_verdict(False)
                elif not self.engine.sieve.pre_filter_claim(expression):
                    verdict = "REJECTED_BY_SIEVE"
                    detail = "numeric claim failed the sieve pre-filter"
                    self.engine.ledger.record_verdict(False)
                else:
                    if claimed is not None:
                        result = self.engine.value(expression, str(claimed))
                        verdict = result["status"]
                        detail = result["detail"]
                        self.engine.ledger.record_verdict(result["status"] in {"PROVED", "VERIFIED", "SUPPORTED"})
                    else:
                        numeric_value = self.engine.evaluate_high_precision_numeric(expression)
                        verdict = "VERIFIED"
                        detail = str(numeric_value)
                        self.engine.ledger.record_verdict(True)

            elif claim_type == "matrix":
                matrix_a = data.get("matrix_a", [])
                matrix_b = data.get("matrix_b", [])
                operation = data.get("operation", "rank")

                if not matrix_a:
                    verdict = "UNKNOWN_CLAIM_TYPE"
                    self.engine.ledger.record_verdict(False)
                else:
                    result = self.engine.matrix_verify(matrix_a, matrix_b, operation)
                    verdict = result["status"]
                    detail = result["detail"]
                    self.engine.ledger.record_verdict(verdict in {"PROVED", "VERIFIED", "SUPPORTED"})

            else:
                verdict = "UNKNOWN_CLAIM_TYPE"
                detail = f"Unsupported claim type: {claim_type}"
                self.engine.ledger.record_verdict(False)

        except Exception as e:
            verdict = "ERROR_RUNTIME_EXCEPTION"
            detail = str(e)
            self.engine.ledger.record_verdict(False)

        execution_time_ms = (time.perf_counter() - start_time) * 1000
        ledger_snapshot = self.engine.ledger.get_summary()

        # Build execution packet telemetry
        result_packet = {
            "claim_id": claim_id,
            "verdict": verdict,
            "detail": detail,
            "execution_time_ms": round(execution_time_ms, 3),
            "current_ledger_reliability": ledger_snapshot["reliability_percentage"],
            "total_processed": ledger_snapshot["total_processed"],
        }

        self.execution_history.append(result_packet)
        return result_packet

    def run_batch_pipeline(self, claims: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Executes a batch collection of mathematical claims sequentially."""
        results = []
        for claim in claims:
            c_id = claim.get("id", "unknown")
            c_type = claim.get("type", "numeric")
            c_data = claim.get("data", {})

            outcome = self.process_claim_cycle(c_id, c_type, c_data)
            results.append(outcome)
        return results
