"""
Agent 22: Urgency Escalation & Unread SLA Monitoring Engine Agent
Monitors time-sensitive notifications and dynamically escalates digest items to notify if unread SLA thresholds approach.
"""

from typing import Dict, Any

class SLAMonitorEscalationAgent:
    def __init__(self, default_sla_minutes: int = 120):
        self.name = "Agent 22: SLA Monitor & Urgency Escalator"
        self.default_sla_minutes = default_sla_minutes

    def evaluate_escalation(self, decision: Dict[str, Any], time_elapsed_minutes: int = 0) -> Dict[str, Any]:
        """
        If a decision is currently 'digest', but the message involves a time-sensitive event, bill,
        or meeting within the SLA window, escalate to 'notify'.
        """
        action = decision.get("action", "")
        message_type = decision.get("message_type", "")
        reason = decision.get("reason", "")

        if action == "digest" and message_type in ["event", "business_update", "urgent"]:
            if time_elapsed_minutes >= self.default_sla_minutes or "today" in reason.lower() or "same-day" in reason.lower():
                escalated_decision = dict(decision)
                escalated_decision["action"] = "notify"
                escalated_decision["reason"] += " (Escalated to notify due to unread SLA deadline approach)."
                escalated_decision["sla_escalated"] = True
                return escalated_decision

        decision_copy = dict(decision)
        decision_copy["sla_escalated"] = False
        return decision_copy
