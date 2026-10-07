"""
NPKmath Test Suite: Verification Signals
Tests the AI signal export layer for knowledge ranking, freshness decay, and feedback.
"""
import pytest
import json
from datetime import datetime, timezone, timedelta
from npkmath.signals import VerificationSignal, AIFeedbackInterface, SignalRanker


class TestVerificationSignal:
    """Test VerificationSignal dataclass and methods."""
    
    def test_signal_creation(self):
        """Test creating a basic verification signal."""
        signal = VerificationSignal(
            claim_id="claim-001",
            claim_type="symbolic",
            status="PROVED",
            confidence=1.0,
            source_reliability=0.9,
            freshness_score=1.0,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        assert signal.claim_id == "claim-001"
        assert signal.confidence == 1.0
        assert signal.effective_weight() == 0.9  # 1.0 * 1.0 * 0.9
    
    def test_signal_to_dict(self):
        """Test signal serialization to dictionary."""
        signal = VerificationSignal(
            claim_id="claim-001",
            claim_type="numeric",
            status="VERIFIED",
            confidence=0.9,
            source_reliability=0.85,
            freshness_score=0.95,
            timestamp=datetime.now(timezone.utc).isoformat(),
            rationale="High-precision verification",
        )
        d = signal.to_dict()
        assert isinstance(d, dict)
        assert d["claim_id"] == "claim-001"
        assert d["rationale"] == "High-precision verification"
    
    def test_signal_to_json(self):
        """Test signal serialization to JSON."""
        signal = VerificationSignal(
            claim_id="claim-001",
            claim_type="symbolic",
            status="PROVED",
            confidence=1.0,
            source_reliability=0.9,
            freshness_score=1.0,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        json_str = signal.to_json()
        assert isinstance(json_str, str)
        parsed = json.loads(json_str)
        assert parsed["claim_id"] == "claim-001"
    
    def test_effective_weight_calculation(self):
        """Test composite weight calculation."""
        signal = VerificationSignal(
            claim_id="claim-001",
            claim_type="symbolic",
            status="PROVED",
            confidence=0.8,
            source_reliability=0.75,
            freshness_score=0.9,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        # 0.8 * 0.75 * 0.9 = 0.54
        assert abs(signal.effective_weight() - 0.54) < 0.01
    
    def test_is_high_confidence_true(self):
        """Test high-confidence filter when signal meets threshold."""
        signal = VerificationSignal(
            claim_id="claim-001",
            claim_type="symbolic",
            status="PROVED",
            confidence=1.0,
            source_reliability=0.85,
            freshness_score=1.0,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        # weight = 1.0 * 0.85 * 1.0 = 0.85, threshold is 0.80
        assert signal.is_high_confidence(threshold=0.80)
    
    def test_is_high_confidence_false(self):
        """Test high-confidence filter when signal does not meet threshold."""
        signal = VerificationSignal(
            claim_id="claim-001",
            claim_type="symbolic",
            status="SUPPORTED",
            confidence=0.7,
            source_reliability=0.5,
            freshness_score=0.7,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        # weight = 0.7 * 0.5 * 0.7 = 0.245, threshold is 0.80
        assert not signal.is_high_confidence(threshold=0.80)
    
    def test_is_fresh_true(self):
        """Test freshness check for recent signal."""
        now = datetime.now(timezone.utc)
        signal = VerificationSignal(
            claim_id="claim-001",
            claim_type="symbolic",
            status="PROVED",
            confidence=1.0,
            source_reliability=0.9,
            freshness_score=1.0,
            timestamp=now.isoformat(),
        )
        assert signal.is_fresh(max_age_hours=24)
    
    def test_is_fresh_false(self):
        """Test freshness check for old signal."""
        old_time = datetime.now(timezone.utc) - timedelta(days=2)
        signal = VerificationSignal(
            claim_id="claim-001",
            claim_type="symbolic",
            status="PROVED",
            confidence=1.0,
            source_reliability=0.9,
            freshness_score=1.0,
            timestamp=old_time.isoformat(),
        )
        assert not signal.is_fresh(max_age_hours=24)


class TestAIFeedbackInterface:
    """Test AIFeedbackInterface emission and export."""
    
    def test_interface_creation(self):
        """Test creating an AI feedback interface."""
        interface = AIFeedbackInterface(max_signal_history=100)
        assert interface.max_history == 100
        assert len(interface.signals) == 0
        assert len(interface.feedback_log) == 0
    
    def test_emit_signal_proved(self):
        """Test emitting a PROVED signal."""
        interface = AIFeedbackInterface()
        signal = interface.emit_signal(
            claim_id="claim-001",
            claim_type="symbolic",
            status="PROVED",
            confidence=1.0,
            source_reliability=0.9,
            rationale="Symbolic simplification",
        )
        assert signal.claim_id == "claim-001"
        assert signal.confidence == 1.0  # Normalized
        assert signal.freshness_score == 1.0  # New signals are fresh
        assert len(interface.signals) == 1
    
    def test_normalize_confidence_proved(self):
        """Test confidence normalization for PROVED status."""
        interface = AIFeedbackInterface()
        # _normalize_confidence is called internally
        signal = interface.emit_signal(
            claim_id="claim-001",
            claim_type="symbolic",
            status="PROVED",
            confidence=0.5,  # Raw value ignored for PROVED
            source_reliability=0.9,
        )
        assert signal.confidence == 1.0  # PROVED maps to 1.0
    
    def test_normalize_confidence_verified(self):
        """Test confidence normalization for VERIFIED status."""
        interface = AIFeedbackInterface()
        signal = interface.emit_signal(
            claim_id="claim-001",
            claim_type="numeric",
            status="VERIFIED",
            confidence=0.5,
            source_reliability=0.9,
        )
        assert signal.confidence == 0.9  # VERIFIED maps to 0.9
    
    def test_normalize_confidence_supported(self):
        """Test confidence normalization for SUPPORTED status."""
        interface = AIFeedbackInterface()
        signal = interface.emit_signal(
            claim_id="claim-001",
            claim_type="symbolic",
            status="SUPPORTED",
            confidence=0.5,
            source_reliability=0.9,
        )
        assert signal.confidence == 0.7  # SUPPORTED maps to 0.7
    
    def test_decay_freshness_recent(self):
        """Test freshness decay for recent signals (1 hour old)."""
        interface = AIFeedbackInterface()
        freshness = interface.decay_freshness(age_hours=1)
        # F(1) = exp(-1/168) ≈ 0.9940
        assert freshness > 0.99
        assert freshness <= 1.0
    
    def test_decay_freshness_one_week(self):
        """Test freshness decay for one-week-old signals."""
        interface = AIFeedbackInterface()
        freshness = interface.decay_freshness(age_hours=168)
        # F(168) = exp(-1) ≈ 0.3679 (half-life at tau)
        assert abs(freshness - 0.3679) < 0.01
    
    def test_decay_freshness_one_month(self):
        """Test freshness decay for one-month-old signals."""
        interface = AIFeedbackInterface()
        freshness = interface.decay_freshness(age_hours=30 * 24)  # 30 days
        # F(720) = exp(-720/168) ≈ 0.0169
        assert freshness < 0.05
        assert freshness > 0
    
    def test_get_fresh_signals_sorted(self):
        """Test retrieving fresh signals sorted by weight."""
        interface = AIFeedbackInterface()
        
        # Emit signals with different weights
        interface.emit_signal(
            claim_id="claim-001",
            claim_type="symbolic",
            status="PROVED",
            confidence=1.0,
            source_reliability=0.9,
        )
        interface.emit_signal(
            claim_id="claim-002",
            claim_type="numeric",
            status="VERIFIED",
            confidence=0.9,
            source_reliability=0.8,
        )
        interface.emit_signal(
            claim_id="claim-003",
            claim_type="symbolic",
            status="SUPPORTED",
            confidence=0.7,
            source_reliability=0.7,
        )
        
        fresh = interface.get_fresh_signals(max_age_hours=24)
        assert len(fresh) == 3
        # Should be sorted by effective_weight descending
        assert fresh[0].effective_weight() >= fresh[1].effective_weight()
        assert fresh[1].effective_weight() >= fresh[2].effective_weight()
    
    def test_get_fresh_signals_with_min_weight(self):
        """Test filtering fresh signals by minimum weight."""
        interface = AIFeedbackInterface()
        
        interface.emit_signal(
            claim_id="claim-001",
            claim_type="symbolic",
            status="PROVED",
            confidence=1.0,
            source_reliability=0.9,
        )
        interface.emit_signal(
            claim_id="claim-002",
            claim_type="symbolic",
            status="SUPPORTED",
            confidence=0.7,
            source_reliability=0.5,
        )
        
        # Filter for weight >= 0.50
        fresh = interface.get_fresh_signals(max_age_hours=24, min_weight=0.50)
        assert len(fresh) >= 1
        assert all(s.effective_weight() >= 0.50 for s in fresh)
    
    def test_get_signals_by_domain(self):
        """Test retrieving signals filtered by domain tag."""
        interface = AIFeedbackInterface()
        
        interface.emit_signal(
            claim_id="claim-001",
            claim_type="symbolic",
            status="PROVED",
            confidence=1.0,
            source_reliability=0.9,
            domain_tags=["math", "symbolic"],
        )
        interface.emit_signal(
            claim_id="claim-002",
            claim_type="numeric",
            status="VERIFIED",
            confidence=0.9,
            source_reliability=0.8,
            domain_tags=["math", "numeric"],
        )
        interface.emit_signal(
            claim_id="claim-003",
            claim_type="symbolic",
            status="SUPPORTED",
            confidence=0.7,
            source_reliability=0.7,
            domain_tags=["physics", "symbolic"],
        )
        
        math_signals = interface.get_signals_by_domain("math", max_age_hours=24)
        assert len(math_signals) == 2
        assert all("math" in s.domain_tags for s in math_signals)
        
        physics_signals = interface.get_signals_by_domain("physics", max_age_hours=24)
        assert len(physics_signals) == 1
        assert "physics" in physics_signals[0].domain_tags
    
    def test_export_for_prompt(self):
        """Test exporting signals in markdown format for LLM prompts."""
        interface = AIFeedbackInterface()
        
        interface.emit_signal(
            claim_id="claim-001",
            claim_type="symbolic",
            status="PROVED",
            confidence=1.0,
            source_reliability=0.9,
            rationale="Symbolic simplification",
            evidence_summary="simplify(L-R) == 0",
        )
        
        prompt_text = interface.export_for_prompt(max_signals=10, max_age_hours=24)
        assert isinstance(prompt_text, str)
        assert "Verified Knowledge" in prompt_text
        assert "claim-001" in prompt_text
        assert "PROVED" in prompt_text
        assert "Symbolic simplification" in prompt_text
    
    def test_export_for_retrieval(self):
        """Test exporting signals in JSON format for retrieval systems."""
        interface = AIFeedbackInterface()
        
        interface.emit_signal(
            claim_id="claim-001",
            claim_type="symbolic",
            status="PROVED",
            confidence=1.0,
            source_reliability=0.9,
        )
        
        retrieval_data = interface.export_for_retrieval(max_age_hours=24)
        assert isinstance(retrieval_data, list)
        assert len(retrieval_data) >= 1
        assert all(isinstance(s, dict) for s in retrieval_data)
        assert retrieval_data[0]["claim_id"] == "claim-001"
    
    def test_log_ai_feedback(self):
        """Test logging feedback from an AI system."""
        interface = AIFeedbackInterface()
        
        interface.log_ai_feedback(
            signal_id="claim-001",
            ai_decision="Used signal to improve reasoning",
            outcome="correct",
            metadata={"model": "gpt-4", "context_length": 8192},
        )
        
        assert len(interface.feedback_log) == 1
        entry = interface.feedback_log[0]
        assert entry["signal_id"] == "claim-001"
        assert entry["outcome"] == "correct"
        assert entry["metadata"]["model"] == "gpt-4"
    
    def test_get_summary(self):
        """Test getting summary statistics."""
        interface = AIFeedbackInterface()
        
        interface.emit_signal(
            claim_id="claim-001",
            claim_type="symbolic",
            status="PROVED",
            confidence=1.0,
            source_reliability=0.9,
        )
        interface.emit_signal(
            claim_id="claim-002",
            claim_type="symbolic",
            status="SUPPORTED",
            confidence=0.7,
            source_reliability=0.5,
        )
        interface.log_ai_feedback("claim-001", "decision", "correct")
        
        summary = interface.get_summary()
        assert summary["total_signals"] == 2
        assert summary["fresh_signals_24h"] >= 2
        assert summary["feedback_log_entries"] == 1
        assert "average_effective_weight" in summary


class TestSignalRanker:
    """Test advanced signal ranking and filtering."""
    
    def test_rank_by_weight_descending(self):
        """Test ranking signals by effective weight (descending)."""
        signals = [
            VerificationSignal(
                claim_id="claim-001",
                claim_type="symbolic",
                status="PROVED",
                confidence=0.7,
                source_reliability=0.7,
                freshness_score=0.7,
                timestamp=datetime.now(timezone.utc).isoformat(),
            ),
            VerificationSignal(
                claim_id="claim-002",
                claim_type="symbolic",
                status="PROVED",
                confidence=1.0,
                source_reliability=0.9,
                freshness_score=1.0,
                timestamp=datetime.now(timezone.utc).isoformat(),
            ),
        ]
        
        ranked = SignalRanker.rank_by_weight(signals, descending=True)
        assert ranked[0].claim_id == "claim-002"  # Higher weight first
        assert ranked[1].claim_id == "claim-001"
    
    def test_filter_by_confidence(self):
        """Test filtering signals by confidence threshold."""
        signals = [
            VerificationSignal(
                claim_id="claim-001",
                claim_type="symbolic",
                status="PROVED",
                confidence=1.0,
                source_reliability=0.9,
                freshness_score=1.0,
                timestamp=datetime.now(timezone.utc).isoformat(),
            ),
            VerificationSignal(
                claim_id="claim-002",
                claim_type="symbolic",
                status="SUPPORTED",
                confidence=0.7,
                source_reliability=0.7,
                freshness_score=1.0,
                timestamp=datetime.now(timezone.utc).isoformat(),
            ),
        ]
        
        filtered = SignalRanker.filter_by_confidence(signals, min_confidence=0.8)
        assert len(filtered) == 1
        assert filtered[0].claim_id == "claim-001"
    
    def test_filter_by_status(self):
        """Test filtering signals by status."""
        signals = [
            VerificationSignal(
                claim_id="claim-001",
                claim_type="symbolic",
                status="PROVED",
                confidence=1.0,
                source_reliability=0.9,
                freshness_score=1.0,
                timestamp=datetime.now(timezone.utc).isoformat(),
            ),
            VerificationSignal(
                claim_id="claim-002",
                claim_type="symbolic",
                status="REFUTED",
                confidence=0.95,
                source_reliability=0.8,
                freshness_score=1.0,
                timestamp=datetime.now(timezone.utc).isoformat(),
            ),
            VerificationSignal(
                claim_id="claim-003",
                claim_type="symbolic",
                status="SUPPORTED",
                confidence=0.7,
                source_reliability=0.7,
                freshness_score=1.0,
                timestamp=datetime.now(timezone.utc).isoformat(),
            ),
        ]
        
        proved_refuted = SignalRanker.filter_by_status(signals, ["PROVED", "REFUTED"])
        assert len(proved_refuted) == 2
        assert all(s.status in ["PROVED", "REFUTED"] for s in proved_refuted)
    
    def test_deduplicate_by_claim(self):
        """Test keeping only highest-weight signal per claim."""
        signals = [
            VerificationSignal(
                claim_id="claim-001",
                claim_type="symbolic",
                status="PROVED",
                confidence=0.9,
                source_reliability=0.8,
                freshness_score=0.8,
                timestamp=datetime.now(timezone.utc).isoformat(),
            ),
            VerificationSignal(
                claim_id="claim-001",  # Same claim ID
                claim_type="symbolic",
                status="VERIFIED",
                confidence=1.0,
                source_reliability=0.9,
                freshness_score=1.0,
                timestamp=datetime.now(timezone.utc).isoformat(),
            ),
            VerificationSignal(
                claim_id="claim-002",
                claim_type="symbolic",
                status="PROVED",
                confidence=1.0,
                source_reliability=0.9,
                freshness_score=1.0,
                timestamp=datetime.now(timezone.utc).isoformat(),
            ),
        ]
        
        deduplicated = SignalRanker.deduplicate_by_claim(signals)
        assert len(deduplicated) == 2
        assert deduplicated["claim-001"].effective_weight() == 1.0 * 1.0 * 0.9  # Highest
        assert deduplicated["claim-002"].effective_weight() == 1.0 * 1.0 * 0.9
