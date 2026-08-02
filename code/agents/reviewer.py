"""
Reviewer Mini-Agents Module: Audits and reviews prediction decisions before output generation.
"""

from typing import Dict, Any

class SafetyAuditorMiniAgent:
    """Mini-Agent 1: Safety & Scam Reviewer"""

    def audit(self, row: Dict[str, Any], decision: Dict[str, Any]) -> Dict[str, Any]:
        text = (row.get("message_text") or "").lower()
        action = decision.get("action")

        # If message contains scam keywords but action was not mute, correct it
        scam_triggers = ["otp", "password", "account block", "qr", "lottery", "verify account access"]
        if any(trig in text for trig in scam_triggers) and action != "mute":
            decision["action"] = "mute"
            decision["message_type"] = "scam"
            decision["reason"] = "Audit Mini-Agent: Overridden to mute due to sensitive verification or scam trigger."
            decision["confidence"] = 0.87

        return decision

class PersonalizationAuditorMiniAgent:
    """Mini-Agent 2: User Preference & Quiet Hours Reviewer"""

    def audit(self, group_eval: Dict[str, Any], decision: Dict[str, Any]) -> Dict[str, Any]:
        # If user has muted this group, downgrade notify -> digest/mute
        if group_eval.get("user_group_muted") and decision.get("action") == "notify":
            decision["action"] = "digest"
            decision["reason"] = "Audit Mini-Agent: Downgraded notify to digest because user has muted this group."
        return decision

class ReviewerOrchestrator:
    """Master Reviewer Mini-Agent Suite"""

    def __init__(self):
        self.safety_auditor = SafetyAuditorMiniAgent()
        self.pref_auditor = PersonalizationAuditorMiniAgent()

    def review_and_correct(self, row: Dict[str, Any], group_eval: Dict[str, Any], decision: Dict[str, Any]) -> Dict[str, Any]:
        d1 = self.safety_auditor.audit(row, decision)
        d2 = self.pref_auditor.audit(group_eval, d1)
        return d2
