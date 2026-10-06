"""
NPKmath Ledger Engine
Bayesian SourceLedger tracking claim reliability scores using Beta distributions.
"""

class SourceLedger:
    def __init__(self):
        # Initialize Bayesian Beta parameters (Successes, Failures)
        self.alpha = 1.0  # Prior successes
        self.beta = 1.0   # Prior failures
        self.total_claims = 0

    def record_verdict(self, is_valid: bool):
        """Updates internal Bayesian ledger metrics based on evaluation results."""
        self.total_claims += 1
        if is_valid:
            self.alpha += 1.0
        else:
            self.beta += 1.0

    def get_reliability_score(self) -> float:
        """
        Calculates the current expected reliability score.
        Formula: Alpha / (Alpha + Beta)
        """
        denominator = self.alpha + self.beta
        if denominator == 0:
            return 0.5
        return self.alpha / denominator

    def get_summary(self) -> dict:
        """Returns a snapshot of the current engine audit log status."""
        return {
            "total_processed": self.total_claims,
            "alpha_score": self.alpha,
            "beta_score": self.beta,
            "reliability_percentage": round(self.get_reliability_score() * 100, 2)
        }
