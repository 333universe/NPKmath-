"""
NPKmath AI Signal Export Example
Demonstrates how the agent emits structured AI-consumable knowledge signals.

This script shows:
- Batch claim verification
- Signal generation for each claim
- Exporting signals for AI consumption (markdown and JSON)
- Ranking signals by freshness and confidence
"""

import json
from npkmath import NPKAutonomousAgent, SignalRanker


def main():
    """Run example claim verification with signal export."""
    
    # Initialize agent with signal interface
    agent = NPKAutonomousAgent(precision=120)
    
    # Define a batch of mathematical claims to verify
    claims = [
        {
            "id": "claim-001",
            "type": "symbolic",
            "data": {
                "expr1": "sin(x)**2 + cos(x)**2",
                "expr2": "1",
            },
        },
        {
            "id": "claim-002",
            "type": "symbolic",
            "data": {
                "expr1": "x + 1",
                "expr2": "x + 2",
            },
        },
        {
            "id": "claim-003",
            "type": "numeric",
            "data": {
                "expression": "pi",
            },
        },
    ]
    
    print("=" * 70)
    print("NPKmath AI Signal Export Example")
    print("=" * 70)
    print()
    
    # Process claims through the agent
    print("[1/4] Processing claims through the agent pipeline...")
    results = agent.run_batch_pipeline(claims)
    print(f"✓ Processed {len(results)} claims")
    print()
    
    # Display raw results with embedded signals
    print("[2/4] Claim Results with Embedded Signals:")
    print("-" * 70)
    for result in results:
        print(f"\nClaim ID: {result['claim_id']}")
        print(f"Verdict: {result['verdict']}")
        print(f"Detail: {result['detail']}")
        print(f"Execution Time: {result['execution_time_ms']}ms")
        print(f"Ledger Reliability: {result['current_ledger_reliability']}%")
        
        if result.get("signal"):
            signal = result["signal"]
            print(f"Signal Status: {signal['status']}")
            print(f"Signal Confidence: {signal['confidence']:.2f}")
            print(f"Signal Freshness: {signal['freshness_score']:.2f}")
            print(f"Effective Weight: {signal['confidence'] * signal['freshness_score'] * signal['source_reliability']:.3f}")
    print()
    
    # Export signals for AI consumption (markdown format)
    print("[3/4] Exporting Signals for LLM Prompting (Markdown):")
    print("-" * 70)
    prompt_export = agent.signal_interface.export_for_prompt(max_signals=10, max_age_hours=24)
    print(prompt_export)
    print()
    
    # Export signals for retrieval systems (JSON format)
    print("[4/4] Exporting Signals for Retrieval Systems (JSON):")
    print("-" * 70)
    retrieval_export = agent.signal_interface.export_for_retrieval(max_age_hours=24)
    print(json.dumps(retrieval_export, indent=2))
    print()
    
    # Get signal interface summary
    summary = agent.signal_interface.get_summary()
    print("Signal Store Summary:")
    print(f"  Total Signals: {summary['total_signals']}")
    print(f"  Fresh Signals (24h): {summary['fresh_signals_24h']}")
    print(f"  High Confidence: {summary['high_confidence_signals']}")
    print(f"  Average Weight: {summary['average_effective_weight']}")
    print()
    
    # Demonstrate signal ranking
    print("=" * 70)
    print("Signal Ranking Example:")
    print("=" * 70)
    signals = agent.signal_interface.get_fresh_signals(max_age_hours=24)
    ranked = SignalRanker.rank_by_weight(signals, descending=True)
    
    print(f"\nTop {len(ranked)} signals by effective weight:\n")
    for i, signal in enumerate(ranked, 1):
        weight = signal.effective_weight()
        print(f"{i}. {signal.claim_id}")
        print(f"   Status: {signal.status}")
        print(f"   Weight: {weight:.4f} (confidence:{signal.confidence:.2f} × freshness:{signal.freshness_score:.2f} × reliability:{signal.source_reliability:.2f})")
        print()


if __name__ == "__main__":
    main()
