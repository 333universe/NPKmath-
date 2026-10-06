"""
NPKmath Verification Playbook
Executable standalone workflow verifying symbolic and numeric engine loops.
"""
from npkmath.agent import NPKAutonomousAgent

def main():
    print("==================================================")
    print("⚡ Initializing NPKmath Autonomous Agent Loop...")
    print("==================================================")
    
    # Instantiate the agent with standard high-precision parameters
    agent = NPKAutonomousAgent(precision=100)
    
    # Set up mock mathematical validation packets
    mock_claims = [
        {
            "id": "CLAIM-001",
            "type": "symbolic",
            "data": {
                "expr1": "x**2 - y**2",
                "expr2": "(x - y)*(x + y)"
            }
        },
        {
            "id": "CLAIM-002",
            "type": "symbolic",
            "data": {
                "expr1": "sin(x)**2 + cos(x)**2",
                "expr2": "1"
            }
        },
        {
            "id": "CLAIM-003",
            "type": "numeric",
            "data": {
                "expression": "sqrt(2)"
            }
        }
    ]
    
    print(f"📥 Feeding {len(mock_claims)} test claims into pipeline...")
    pipeline_results = agent.run_batch_pipeline(mock_claims)
    
    print("\n📊 Verification Pipeline Execution Results:")
    for result in pipeline_results:
        print(f"--------------------------------------------------")
        print(f"▪️ Claim ID : {result['claim_id']}")
        print(f"▪️ Verdict  : {result['verdict']}")
        print(f"▪️ Exec Time: {result['execution_time_ms']} ms")
        if result['detail']:
            print(f"▪️ Evaluation: {result['detail'][:60]}...")
            
    print(f"--------------------------------------------------")
    print("\n📈 Final Bayesian Ledger Health Check:")
    final_snapshot = agent.engine.ledger.get_summary()
    print(f"▪️ Total Audited Claims : {final_snapshot['total_processed']}")
    print(f"▪️ Reliability Index    : {final_snapshot['reliability_percentage']}%")
    print("==================================================")

if __name__ == "__main__":
    main()
      
