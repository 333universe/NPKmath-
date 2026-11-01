"""
Example usage for NPKmath.
"""

from npkmath import (
    NPKAutonomousAgent,
    run_batch_verification,
    verify_identity,
    verify_matrix,
    verify_value,
)

if __name__ == "__main__":
    print("Symbolic identity check:")
    print(verify_identity("(x + 1)^2", "x^2 + 2*x + 1"))

    print("\nNumeric verification:")
    print(verify_value("sin(pi/6)", claimed="0.5"))

    print("\nMatrix verification:")
    print(
        verify_matrix(
            [["1", "0"], ["0", "1"]],
            operation="invertible",
        )
    )

    print("\nBatch pipeline:")
    claims = [
        {
            "id": "claim-1",
            "type": "numeric",
            "data": {"expression": "sqrt(16)", "claimed": "4"},
        },
        {
            "id": "claim-2",
            "type": "identity",
            "data": {"lhs": "(x + 1)^2", "rhs": "x^2 + 2*x + 1"},
        },
    ]
    print(run_batch_verification(claims))

    print("\nDirect agent usage:")
    agent = NPKAutonomousAgent(precision=120)
    result = agent.process_claim_cycle(
        "demo-claim",
        "numeric",
        {"expression": "sqrt(9)", "claimed": "3"},
    )
    print(result)
