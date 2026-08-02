"""
Agent 21: Smart Action & One-Tap Quick Reply Generator Agent
Generates 2-3 contextual interactive quick actions for incoming WhatsApp messages.
"""

from typing import Dict, Any, List

class QuickReplyGeneratorAgent:
    def __init__(self):
        self.name = "Agent 21: Quick Reply & Smart Action Generator"

    def generate_actions(self, message_text: str, action: str, message_type: str) -> List[str]:
        text_lower = (message_text or "").lower()

        if action == "mute":
            if message_type == "scam":
                return ["Report & Block", "Ignore"]
            elif message_type == "promotion":
                return ["Unsubscribe", "Mute Sender"]
            elif message_type == "forward":
                return ["Mute Group", "Dismiss"]
            else:
                return ["Dismiss"]

        if message_type == "urgent":
            if "call" in text_lower or "ping" in text_lower:
                return ["Call Back", "Reply: 'On my way'", "Busy right now"]
            elif "meeting" in text_lower or "review" in text_lower or "prod" in text_lower:
                return ["Join Meeting", "Acknowledge", "Reschedule"]
            else:
                return ["Respond Now", "Snooze 15m", "Mark Done"]

        if message_type == "event":
            return ["Add to Calendar", "Confirm RSVP", "Decline"]

        if message_type == "business_update":
            if "delivery" in text_lower or "order" in text_lower:
                return ["Track Order", "Delivery Notes"]
            elif "bill" in text_lower or "invoice" in text_lower or "payment" in text_lower:
                return ["Pay Invoice", "View Receipt"]
            else:
                return ["View Details", "Archive"]

        if message_type == "personal":
            return ["Reply", "Send Emoji 👍", "Snooze"]

        if message_type == "promotion":
            return ["View Deal", "Save for Later", "Opt-out"]

        return ["Reply", "Dismiss"]
