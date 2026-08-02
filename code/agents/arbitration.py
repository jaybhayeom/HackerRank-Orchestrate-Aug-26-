"""
Layer 4: Consensus, Decision Arbitration & Quality Assurance Agents
"""

import csv
import os
from typing import Dict, Any, List

class DecisionArbiterAgent:
    """Agent 12: Decision Arbiter & Reason Synthesizer Agent"""

    ALLOWED_ACTIONS = {"notify", "digest", "mute"}
    ALLOWED_TYPES = {
        "personal", "urgent", "event", "payment", "business_update",
        "promotion", "greeting", "forward", "spam", "scam", "unknown"
    }

    def __init__(self):
        self.name = "Agent 12: Decision Arbiter"

    def arbitrate(
        self,
        row: Dict[str, Any],
        threat_eval: Dict[str, Any],
        urgency_eval: Dict[str, Any],
        utility_eval: Dict[str, Any],
        marketing_eval: Dict[str, Any],
        evidence_eval: Dict[str, Any],
        llm_decision: Dict[str, Any] = None
    ) -> Dict[str, Any]:

        # 1. Threat override (Highest Priority)
        if threat_eval.get("is_threat"):
            return {
                "message_id": row.get("message_id"),
                "action": threat_eval.get("action", "mute"),
                "message_type": threat_eval.get("message_type", "scam"),
                "reason": threat_eval.get("reason"),
                "confidence": threat_eval.get("confidence", 0.85),
                "evidence_message_ids": evidence_eval.get("evidence_message_ids", "none")
            }

        # 2. Urgency Priority
        if urgency_eval.get("is_urgent"):
            return {
                "message_id": row.get("message_id"),
                "action": urgency_eval.get("action", "notify"),
                "message_type": urgency_eval.get("message_type", "urgent"),
                "reason": urgency_eval.get("reason"),
                "confidence": urgency_eval.get("confidence", 0.87),
                "evidence_message_ids": evidence_eval.get("evidence_message_ids", "none")
            }

        # 3. Transactional Utility Priority
        if utility_eval.get("is_utility"):
            return {
                "message_id": row.get("message_id"),
                "action": utility_eval.get("action", "notify"),
                "message_type": utility_eval.get("message_type", "business_update"),
                "reason": utility_eval.get("reason"),
                "confidence": utility_eval.get("confidence", 0.89),
                "evidence_message_ids": evidence_eval.get("evidence_message_ids", "none")
            }

        # 4. Marketing Priority
        if marketing_eval.get("is_marketing"):
            return {
                "message_id": row.get("message_id"),
                "action": marketing_eval.get("action", "digest"),
                "message_type": marketing_eval.get("message_type", "promotion"),
                "reason": marketing_eval.get("reason"),
                "confidence": marketing_eval.get("confidence", 0.81),
                "evidence_message_ids": evidence_eval.get("evidence_message_ids", "none")
            }

        # 5. Bonus LLM Deferral Layer (if LLM returned a confident decision)
        if llm_decision and isinstance(llm_decision, dict) and llm_decision.get("confidence", 0) >= 0.60:
            return {
                "message_id": row.get("message_id"),
                "action": llm_decision.get("action", "digest"),
                "message_type": llm_decision.get("message_type", "personal"),
                "reason": llm_decision.get("reason", "LLM reasoning analysis."),
                "confidence": float(llm_decision.get("confidence", 0.85)),
                "evidence_message_ids": evidence_eval.get("evidence_message_ids", "none")
            }

        # 6. Structured Signal & Default Digest / Personal Fallback
        text = (row.get("message_text") or "").lower()
        conv_type = row.get("conversation_type")
        biz_id = row.get("business_id")

        if "good morning" in text or "smiling" in text:
            action = "digest" if row.get("forwarded_count", 0) == 0 else "mute"
            msg_type = "greeting"
            reason = "The message is a harmless greeting that can be read later."
        elif conv_type == "group" and not biz_id:
            action = "digest"
            msg_type = "personal"
            reason = "Safe non-urgent group conversation or peer notice."
        elif biz_id:
            action = "digest"
            msg_type = "business_update"
            reason = "Routine business notice or transactional update."
        elif conv_type in ["personal", "direct"]:
            action = "digest"
            msg_type = "personal"
            reason = "The sender is trusted, but the message has no urgent action or safety relevance."
        else:
            action = "digest"
            msg_type = "unknown"
            reason = "The message is safe, but does not require immediate attention."

        return {
            "message_id": row.get("message_id"),
            "action": action,
            "message_type": msg_type,
            "reason": reason,
            "confidence": 0.82,
            "evidence_message_ids": evidence_eval.get("evidence_message_ids", "none")
        }

class SchemaValidatorAgent:
    """Agent 13: Schema Validation & Compliance Quality Agent"""

    def __init__(self):
        self.name = "Agent 13: Schema Validator"

    def validate(self, output_row: Dict[str, Any]) -> Dict[str, Any]:
        cleaned = dict(output_row)

        # Enforce valid action
        if cleaned.get("action") not in {"notify", "digest", "mute"}:
            cleaned["action"] = "digest"

        # Enforce valid message_type
        if cleaned.get("message_type") not in {
            "personal", "urgent", "event", "payment", "business_update",
            "promotion", "greeting", "forward", "spam", "scam", "unknown"
        }:
            cleaned["message_type"] = "unknown"

        # Enforce confidence calibration
        try:
            conf = float(cleaned.get("confidence", 0.80))
            cleaned["confidence"] = round(max(0.0, min(1.0, conf)), 2)
        except Exception:
            cleaned["confidence"] = 0.80

        # Enforce evidence fallback
        ev = cleaned.get("evidence_message_ids")
        if not ev or str(ev).strip() == "":
            cleaned["evidence_message_ids"] = "none"

        return cleaned

import traceback

class FallbackResilienceAgent:
    """Agent 20: Fallback & OOV Resilience Agent"""

    def __init__(self):
        self.name = "Agent 20: Fallback Resilience"

    def handle_exception(self, msg_id: str, err: Exception) -> Dict[str, Any]:
        tb_str = traceback.format_exc()
        log_file = os.path.expanduser("~/hackerrank_orchestrate_august26/log.txt")
        try:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"\n[FALLBACK EXCEPTION] Msg ID: {msg_id} | Err: {str(err)}\n{tb_str}\n")
        except Exception:
            pass

        return {
            "message_id": msg_id,
            "action": "digest",
            "message_type": "unknown",
            "reason": f"Fallback applied due to input processing constraint: {str(err)}",
            "confidence": 0.50,
            "evidence_message_ids": "none"
        }
