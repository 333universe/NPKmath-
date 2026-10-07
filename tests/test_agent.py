"""
NPKmath Verification Playbook
Executable standalone workflow verifying production engine identity, value,
and matrix calculation loops dynamically.
"""
from npkmath.agent import NPKAutonomousAgent


def main():
    print("==================================================")
    print("⚡ Initializing NPKmath Production Agent Loop...")
    print("==================================================")

    # Instantiate the agent with standard high-precision parameters
    agent = NPKAutonomousAgent(precision=100)

    # Use the actual agent contract: symbolic and numeric claim packets
    mock_claims = [
        {
            "id": "CLAIM-001",
            "type": "symbolic",
            "data": {
                "expr1": "sin(x)**2 + cos(x)**2",
                "expr2": "1",
                "source": "automated-trig-suite",
            },
        },
        {
            "id": "CLAIM-002",
            "type": "numeric",
            "data": {
                "expression": "pi",
                "claimed": "3.14159",
                "source": "approximations-log",
            },
        },
        {
            "id": "CLAIM-003",
            "type": "symbolic",
            "data": {
                "expr1": "x + 1",
                "expr2": "x + 2",
                "source": "counter-check-false",
            },
        },
        {
            "id": "CLAIM-004",
            "type": "matrix",
            "data": {
                "matrix_a": [["1", "2"], ["2", "4"]],
                "matrix_b": [],
                "operation": "rank",
                "source": "linear-algebra-check",
            },
        },
    ]

    print(f"📥 Feeding {len(mock_claims)} core test claims into agent pipeline...\n")

    results = agent.run_batch_pipeline(mock_claims)

    for result in results:
        print(f"--------------------------------------------------")
        print(f"▪️ Claim ID        : {result['claim_id']}")
        print(f"▪️ Verdict         : {result['verdict']}")
        print(f"▪️ Detail          : {result['detail']}")
        print(f"▪️ Execution Time  : {result['execution_time_ms']:.3f} ms")
        print(f"▪️ Ledger Score   : {result['current_ledger_reliability']:.2f}%")
        print(f"▪️ Total Processed : {result['total_processed']}")

    print("\n" + "=" * 50)
    print("📈 Final Bayesian Source Ledger Assessment:")
    summary = agent.engine.ledger.get_summary()
    print(f"  Total Claims Processed: {summary['total_processed']}")
    print(f"  Verified (Alpha)     : {summary['alpha_score']}")
    print(f"  Flagged (Beta)       : {summary['beta_score']}")
    print(f"  Reliability Score    : {summary['reliability_percentage']:.2f}%")
    print("=" * 50)


if __name__ == "__main__":
    main()
