"""
theory.py - Number Theory Knowledge Ingestion & Epistemic Verification Layer
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Tuple
import sympy as sp
from npkmath.ledger import SourceLedger
from npkmath.sieve import GoldenSieve

@dataclass
class KnowledgeClaim:
    claim_id: str
    source_id: str
    property_type: str        # e.g., "primality", "composite"
    expression_str: str       # Raw string input to be processed securely by the sieve
    meta_payload: Dict[str, Any] = field(default_factory=dict)

class NumberTheoryEngine:
    def __init__(self, sieve: GoldenSieve):
        self.sieve = sieve
        # System Knowledge Base of verified exact truths
        self.verified_knowledge: Dict[sp.Basic, Dict[str, bool]] = {}
        # Registry mapping source IDs to their respective SourceLedger profiles
        self.registry: Dict[str, SourceLedger] = {}

    def get_or_create_ledger(self, source_id: str) -> SourceLedger:
        """Retrieves or initializes a Bayesian ledger for a given data source."""
        if source_id not in self.registry:
            self.registry[source_id] = SourceLedger()
        return self.registry[source_id]

    def ingest_new_knowledge(self, claim: KnowledgeClaim) -> Tuple[bool, float]:
        """
        Ingests a raw mathematical claim string, filters and parses it via GoldenSieve,
        executes algorithmic validations, and updates the source's Bayesian ledger profile.
        """
        ledger = self.get_or_create_ledger(claim.source_id)
        
        # Step 1: Baseline textual pre-filtering
        if not self.sieve.pre_filter_claim(claim.expression_str):
            ledger.record_verdict(False)
            return False, ledger.get_reliability_score()

        # Step 2: Safe algebraic parsing into a true SymPy entity
        try:
            parsed_expr = self.sieve.parse_expression(claim.expression_str)
        except Exception:
            # If parsing fails or malicious syntax is blocked, fail gracefully
            ledger.record_verdict(False)
            return False, ledger.get_reliability_score()

        # Step 3: Evidentiary Verification Loop
        is_valid = self._verify_expression(parsed_expr, claim.property_type)
        
        # Step 4: Record verdict inside the Bayesian Beta distribution tracker
        ledger.record_verdict(is_valid)
        
        # Step 5: Commit to persistent knowledge framework upon absolute proof
        if is_valid:
            if parsed_expr not in self.verified_knowledge:
                self.verified_knowledge[parsed_expr] = {}
            self.verified_knowledge[parsed_expr][claim.property_type] = True
            
        return is_valid, ledger.get_reliability_score()

    def _verify_expression(self, expr: sp.Basic, property_type: str) -> bool:
        """Internal algorithmic truth-gate handling parsed SymPy structures."""
        # Ensure we are evaluating a concrete integer entity for number theory module
        if not expr.is_Integer:
            return False
            
        target_value = int(expr)
        
        if property_type == "primality":
            return sp.isprime(target_value)
        elif property_type == "composite":
            return not sp.isprime(target_value) and target_value > 1
        
        return False
        
