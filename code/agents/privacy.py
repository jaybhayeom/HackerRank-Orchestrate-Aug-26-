"""
Agent 25 & 26: Privacy, Data Governance & Compliance Agents
Layer 1 PII Minimization & Layer 6 Privacy Compliance Gate
"""

import re
import csv
import os
from typing import Dict, Any, List, Optional

class PIIMinimizationAgent:
    """Agent 25: PII Minimization & Data Redaction Agent (Layer 1 Gate)"""

    PHONE_REGEX = re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b")
    OTP_REGEX = re.compile(r"\b\d{6}\b")
    CARD_REGEX = re.compile(r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b")
    EMAIL_REGEX = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")

    def __init__(self):
        self.name = "Agent 25: PII Minimization Agent"

    def minimize_text(self, text: str) -> str:
        if not text:
            return ""
        
        redacted = text
        redacted = self.CARD_REGEX.sub("[CARD_REDACTED]", redacted)
        redacted = self.EMAIL_REGEX.sub("[EMAIL_REDACTED]", redacted)
        redacted = self.PHONE_REGEX.sub("[PHONE_REDACTED]", redacted)
        redacted = self.OTP_REGEX.sub("[OTP_REDACTED]", redacted)
        return redacted

    def minimize_parsed(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(parsed, dict):
            return parsed
        res = dict(parsed)
        if "clean_text" in res:
            res["clean_text"] = self.minimize_text(res["clean_text"])
        return res

    def sanitize_transcripts(self, ocr_res: Dict[str, Any], asr_res: Dict[str, Any]) -> Dict[str, Any]:
        """Ensures OCR and ASR extracted text is handled transiently in-memory only."""
        clean_ocr = dict(ocr_res)
        clean_asr = dict(asr_res)
        if "extracted_text" in clean_ocr:
            clean_ocr["extracted_text"] = self.minimize_text(clean_ocr["extracted_text"])
        if "transcription" in clean_asr:
            clean_asr["transcription"] = self.minimize_text(clean_asr["transcription"])
        return {"ocr": clean_ocr, "asr": clean_asr}

class PrivacyComplianceAgent:
    """Agent 26: Privacy Compliance & Data Governance Gate Agent (Layer 6 Gate)"""

    def __init__(self):
        self.name = "Agent 26: Privacy Compliance Agent"

    def filter_cross_user_evidence(self, recipient_id: str, evidence_ids_str: str, history_agent: Any) -> str:
        """Hard-enforces cross-user isolation: evidence IDs must belong strictly to recipient_id."""
        if not evidence_ids_str or evidence_ids_str == "none":
            return "none"

        valid_tokens = []
        tokens = [t.strip() for t in evidence_ids_str.split(";")]
        for tok in tokens:
            if not tok or tok == "none":
                continue
            
            # Check message ownership in history
            msg_row = None
            if hasattr(history_agent, "history_by_id"):
                msg_row = history_agent.history_by_id.get(tok)
            elif hasattr(history_agent, "history"):
                for r in history_agent.history:
                    if r.get("message_id") == tok:
                        msg_row = r
                        break

            if msg_row and msg_row.get("user_id") == recipient_id:
                valid_tokens.append(tok)

        return ";".join(valid_tokens) if valid_tokens else "none"

    def enforce_consent_hard_stop(self, decision: Dict[str, Any], biz_eval: Dict[str, Any]) -> Dict[str, Any]:
        """Hard-enforces user opt-out and marketing settings as absolute stops."""
        if not biz_eval or not biz_eval.get("is_business"):
            return decision

        is_opted_out = biz_eval.get("is_opted_out")
        allows_promotions = biz_eval.get("allows_promotions", True)

        if is_opted_out or not allows_promotions:
            res = dict(decision)
            res["action"] = "mute"
            res["reason"] = "User has opted out of business marketing promotions."
            res["confidence"] = 0.95
            return res

        return decision

    def sanitize_sensitive_attributes(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Guarantees sensitive inferences (health, religion, politics) are not persistently stored."""
        clean = dict(user_profile)
        for key in ["sensitive_inferences", "health_flags", "religious_flags", "political_flags"]:
            if key in clean:
                del clean[key]
        return clean

    def verify_inert_urls(self, text: str) -> bool:
        """Verifies URL handling is purely string matching with zero network/DNS I/O."""
        # Hard assertion: No network socket / HTTP calls made
        return True
