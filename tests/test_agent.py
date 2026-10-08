from npkmath.agent import NPKAutonomousAgent


def test_agent_batch_pipeline_handles_symbolic_and_numeric_claims():
    agent = NPKAutonomousAgent()

    results = agent.run_batch_pipeline([
        {
            "id": "CLAIM-001",
            "type": "symbolic",
            "data": {"expr1": "sin(x)**2 + cos(x)**2", "expr2": "1"},
        },
        {
            "id": "CLAIM-002",
            "type": "numeric",
            "data": {"expression": "pi", "claimed": "3.14159"},
        },
    ])

    assert [result["verdict"] for result in results] == ["PROVED", "VERIFIED"]
    assert results[0]["total_processed"] == 1
    assert results[1]["total_processed"] == 2


def test_agent_rejects_malicious_symbolic_payloads_gracefully():
    agent = NPKAutonomousAgent()

    result = agent.process_claim_cycle(
        "CLAIM-003",
        "symbolic",
        {"expr1": "eval('1 + 1')", "expr2": "2"},
    )

    assert result["verdict"] in {"REJECTED_BY_SIEVE", "ERROR_RUNTIME_EXCEPTION"}
    assert result["total_processed"] >= 1


def test_agent_tracks_ledger_progression():
    agent = NPKAutonomousAgent()

    agent.process_claim_cycle(
        "CLAIM-1",
        "symbolic",
        {"expr1": "sin(x)**2 + cos(x)**2", "expr2": "1"},
    )

    agent.process_claim_cycle(
        "CLAIM-2",
        "symbolic",
        {"expr1": "x + 1", "expr2": "x + 2"},
    )

    summary = agent.engine.ledger.get_summary()
    assert summary["total_processed"] == 2
    assert summary["reliability_percentage"] in {33.33, 50.0, 66.67}
