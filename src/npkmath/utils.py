"""
NPKmath Utility Module
Provides production telemetry logs, performance metrics, and serialization helpers.
"""
import json
import time
from typing import Dict, Any

def format_telemetry_packet(claim_id: str, verdict: str, metrics: Dict[str, Any]) -> str:
    """
    Serializes mathematical verification results into standard JSON format.
    Perfect for streaming telemetry data safely to external open-source pipelines.
    """
    packet = {
        "timestamp": int(time.time()),
        "claim_id": claim_id,
        "verdict": verdict,
        "performance": metrics
    }
    try:
        return json.dumps(packet, sort_keys=True)
    except (TypeError, ValueError) as e:
        return json.dumps({"error": f"Failed to serialize packet data: {str(e)}"})

def calculate_time_delta_ms(start_counter: float) -> float:
    """Calculates precision runtime intervals in milliseconds."""
    return round((time.perf_counter() - start_counter) * 1000, 3)
