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
    
    # Set up mock mathematical validation packets containing our new modules
    mock_claims = [
        {
            "id": "CLAIM-001",
            "type": "identity",
            "data": {
                "lhs": "sin(x)**2 + cos(x)**2",
                "rhs": "1",
                "source": "automated-trig-suite"
            }
        },
        {
            "id": "CLAIM-002",
            "type": "value",
            "data": {
                "expr": "pi",
                "claimed": "3.14159",
                "source": "approximations-log"
            }
        },
        {
            "id": "CLAIM-003",
            "type": "dimensions",
            "data": {
                "equation": "F = m*a",
                "dims": {"F": "M L T^-2", "m": "M", "a": "L T^-2"},
                "source": "physics-unit-audit"
            }
        },
        {
            "id": "CLAIM-004",
            "type": "matrix",  # Direct integration test for our linear algebra engine extension
            "data": {
                "matrix_a": [["1", "2"], ["2", "4"]],
                "matrix_b": [],
                "operation": "rank",
                "source": "linear-algebra-check"
            }
        }
    ]
    
    print(f"📥 Feeding {len(mock_claims)} core test claims into agent pipeline...")
    
    # Process the pipeline via the structural routing loop
    for claim in mock_claims:
        c_id = claim["id"]
        c_type = claim["type"]
        c_data = claim["data"]
        
        # Matrix features hit the core directly, others map through standard agent routing
        if c_type == "matrix":
            res = agent.engine.matrix_verify(c_data["matrix_a"], c_data["matrix_b"], c_data["operation"])
            verdict = res["status"]
            detail = res["detail"]
            exec_time = 0.5  # placeholder execution duration read
        else:
            res = agent.process_claim_cycle(c_id, c_type, c_data)
            verdict = res["verdict"]
            detail = res["detail"]
            exec_time = res["execution_time_ms"]
            
        print(f"--------------------------------------------------")
        print(f"▪️ Claim ID : {c_id} ({c_type.upper()})")
        print(f"▪️ Verdict  : {verdict}")
        print(f"▪️ Detail   : {detail}")
            
    print("==================================================")
    print("📈 Final Bayesian Source Ledger Assessment:")
    # Pull statistical snapshot tracking records processed in this runtime cycle
    for source, t, f, o, r in agent.engine.ledger.table():
        print(f"  {source:<25} Verified: {t} | Flagged: {f} | Reliability: {r:.2%}")
    print("==================================================")

if __name__ == "__main__":
    main()
        
