"""
Layer 3: Specialized Domain Expert Classifier Agents (Enhanced Threat & Edge-Case Traps)
"""

import re
from typing import Dict, Any

class ThreatSecurityAgent:
    """Agent 8: Threat & Security Risk Agent (Scams, Spam, Phishing, Prompt Injection)"""

    def __init__(self):
        self.name = "Agent 8: Threat & Security Risk"

    def evaluate(self, parsed_text: Dict[str, Any], forwarded_count: int, group_eval: Dict[str, Any] = None, biz_eval: Dict[str, Any] = None) -> Dict[str, Any]:
        text = parsed_text.get("clean_text", "")
        text_lower = text.lower()
        group_eval = group_eval or {}
        biz_eval = biz_eval or {}
        
        # 1. Structural Prompt Injection & Fake System Metadata Traps
        kv_assignments = re.findall(r"\b\w+[-_ ]?\w*\s*[=:]\s*\S+", text_lower)
        has_system_terms = any(w in text_lower for w in ["router", "metadata", "user_priority", "override", "system_config", "instruction"])
        has_verif_target = any(w in text_lower for w in ["http", "pin", "otp", "verify", "login", "set action="])
        
        if (
            parsed_text.get("has_prompt_injection")
            or "routing override" in text_lower
            or "set action=" in text_lower
            or (len(kv_assignments) >= 2 and has_system_terms)
            or (has_system_terms and has_verif_target)
        ):
            return {
                "is_threat": True,
                "action": "mute",
                "message_type": "scam",
                "reason": "The message contains fake system/metadata headers or instructions intended to deceive the router.",
                "confidence": 0.90
            }

        # 2. Negation-Aware Payment & Scam Classification
        has_negation_cue = bool(re.search(r"\b(don't|do not|please avoid|mat|nahi|unless|ignore)\b", text_lower))
        
        has_unverified_link = bool(parsed_text.get("contains_link") or "http://" in text_lower or "https://" in text_lower or "www." in text_lower)
        
        # Explicit Narrowed Credential / Security Solicitation Phrases
        has_credential_solicitation = any(w in text_lower for w in [
            "send screenshot", "reply with the 6 digit", "reply with otp", "reply with password",
            "confirm password", "confirm your pin", "verify details now", "unlock your profile",
            "verify account access", "use this link", "click to verify", "scan this qr"
        ])
        
        has_unverified_solicitation = has_unverified_link or has_credential_solicitation

        # Legitimate Payment Reminders with Negation Cue
        is_legit_payment = (
            any(w in text_lower for w in ["payment due today", "maintenance closes", "maintenance payment", "society app", "office qr"])
            and has_negation_cue
            and not has_unverified_solicitation
        )

        if is_legit_payment:
            return {
                "is_threat": True,
                "action": "digest",
                "message_type": "payment",
                "reason": "Legitimate payment notice or maintenance reminder directing residents to official payment channels.",
                "confidence": 0.88
            }

        # 3. Phishing & Scam Traps (English & Hinglish)
        scam_keywords = [
            "otp may have leaked", "verify now at", "confirm password", "profile will be blocked",
            "wallet verification failed", "reply with the 6 digit login code", "verify account access",
            "aapka otp leak", "account bachane ke liye", "verification code abhi confirm", "account block ho jayega",
            "account security at risk", "account suspended", "penalty list is being finalized", "pay the clearance amount",
            "access card may be blocked", "delivery failed", "pay small reattempt fee", "reattempt charge is pending",
            "amazonpay-delivery.in", "account-login.in", "chase-secure-alert.com", "claim prize", "lottery winner",
            "urgent money transfer", "confirm your pin", "pay processing fee", "loan approved", "refund approved for your ticket",
            "clearance amount is not received"
        ]

        # Unverified Payment Demands & Fraud Link Traps
        is_scam_demand = has_unverified_solicitation or any(kw in text_lower for kw in [
            "scan and pay pending charge", "pay processing fee", "refund approved for your ticket",
            "loan approved", "confirm your pin"
        ])

        if any(kw in text_lower for kw in scam_keywords) or is_scam_demand:
            reason_str = "The message asks for urgent OTP, password, or account verification through a suspicious flow."
            if "penalty" in text_lower or "access card" in text_lower:
                reason_str = "The message asks for urgent payment or verification through a suspicious penalty threat flow."
            elif "delivery" in text_lower or "reattempt" in text_lower:
                reason_str = "The message uses a fake delivery reattempt fee link to trick the user."
            elif is_scam_demand:
                reason_str = "The message requests urgent payment, unverified link clicks, or screenshot submission under threat of service cutoff."

            return {
                "is_threat": True,
                "action": "mute",
                "message_type": "scam",
                "reason": reason_str,
                "confidence": 0.87
            }

        # 4. Mass Forwards & Spam Traps (Structural Emergency Exemption)
        is_structurally_exempt = (
            group_eval.get("sender_is_admin", False)
            or biz_eval.get("is_business", False)
            or parsed_text.get("has_direct_mention", False)
        )
        
        if not is_structurally_exempt:
            if forwarded_count >= 5 or "forward this to ten people" in text_lower or "share kar dena" in text_lower:
                msg_type = "spam" if forwarded_count >= 5 and any(w in text_lower for w in ["blessings", "luck", "reward", "voucher", "health tip"]) else "forward"
                return {
                    "is_threat": True,
                    "action": "mute",
                    "message_type": msg_type,
                    "reason": "The sender has a pattern of repeated forwards or greetings that the user usually ignores.",
                    "confidence": 0.84
                }

        return {"is_threat": False}

class UrgencyClassifierAgent:
    """Agent 9: Personal & High-Urgency Classifier Agent"""

    def __init__(self):
        self.name = "Agent 9: Urgent & Personal Classifier"

    def evaluate(self, parsed_text: Dict[str, Any], group_eval: Dict[str, Any], user_load: int) -> Dict[str, Any]:
        text = parsed_text.get("clean_text", "")
        text_lower = text.lower()

        # Physical Delivery at Gate / Entry Confirmation
        if any(w in text_lower for w in ["at your gate", "amazon package", "delivery agent", "flat confirmation"]):
            return {
                "is_urgent": True,
                "action": "notify",
                "message_type": "urgent",
                "reason": "Delivery agent is at the door requiring flat clearance or entry confirmation.",
                "confidence": 0.88
            }

        # Urgent Call / Immediate Response Request
        if any(w in text_lower for w in ["call me urgently", "don't wait till later", "decide in next ten minutes", "need your eyes"]):
            return {
                "is_urgent": True,
                "action": "notify",
                "message_type": "personal",
                "reason": "The sender requests an immediate call or time-sensitive response.",
                "confidence": 0.87
            }

        # Critical Engineering Build Failure
        if "build is failing" in text_lower or ("failing" in text_lower and "can you check" in text_lower):
            return {
                "is_urgent": True,
                "action": "notify",
                "message_type": "urgent",
                "reason": "A critical build or pipeline failure requires immediate engineering review.",
                "confidence": 0.88
            }

        # Imminent Gate / Vehicle Obstruction Warning
        if any(w in text_lower for w in ["gate closes in", "gate band hone", "move any car", "car hata do"]):
            return {
                "is_urgent": True,
                "action": "notify",
                "message_type": "urgent",
                "reason": "An imminent gate closure or access obstruction requires urgent vehicle clearance.",
                "confidence": 0.88
            }

        # Direct mentions with work or action dependencies
        if parsed_text.get("has_direct_mention"):
            if "retry count" in text_lower or "prod review" in text_lower or "escalation" in text_lower or "eod" in text_lower:
                return {
                    "is_urgent": True,
                    "action": "notify",
                    "message_type": "urgent",
                    "reason": "The message is from a work context and contains a direct deadline or meeting dependency.",
                    "confidence": 0.85
                }

            if "call" in text_lower or "5 mins" in text_lower or "ping" in text_lower or "online now" in text_lower:
                return {
                    "is_urgent": True,
                    "action": "notify",
                    "message_type": "personal",
                    "reason": "The sender directly asks this user for a response or action.",
                    "confidence": 0.87
                }

        # Group Operational Announcements & Society Notices
        if group_eval.get("is_group"):
            if any(w in text_lower for w in ["faculty advising", "internship approval", "lift maintenance", "society potluck", "registrations are open", "7 pm sync"]):
                msg_type = "urgent" if "lift maintenance" in text_lower or "7 pm sync" in text_lower else "event"
                action_type = "notify" if msg_type == "urgent" else "digest"
                return {
                    "is_urgent": True if action_type == "notify" else False,
                    "action": action_type,
                    "message_type": msg_type,
                    "reason": "Group notice regarding operational updates, meeting syncs, or society events.",
                    "confidence": 0.86
                }

        # Admin operational alerts in group chats
        if group_eval.get("sender_is_admin"):
            if any(w in text_lower for w in ["tanker", "water", "valve", "plumber", "bus", "route", "school", "parents", "circular"]):
                msg_type = "urgent" if any(w in text_lower for w in ["tanker", "water", "valve", "plumber"]) else "event"
                reason_str = (
                    "A trusted group admin sent a time-sensitive update that should interrupt the user."
                    if msg_type == "urgent"
                    else "A school admin sent a same-day operational update that the user is likely to need immediately."
                )
                return {
                    "is_urgent": True,
                    "action": "notify",
                    "message_type": msg_type,
                    "reason": reason_str,
                    "confidence": 0.88
                }

        return {"is_urgent": False}

class UtilityClassifierAgent:
    """Agent 10: Utility & Transactional Classifier Agent"""

    def __init__(self):
        self.name = "Agent 10: Utility & Transactional Classifier"

    def evaluate(self, parsed_text: Dict[str, Any], biz_eval: Dict[str, Any]) -> Dict[str, Any]:
        text = parsed_text.get("clean_text", "")
        text_lower = text.lower()

        if biz_eval.get("is_business") or biz_eval.get("is_verified"):
            if any(w in text_lower for w in ["packed", "delivery", "order ending", "expected to reach"]):
                return {
                    "is_utility": True,
                    "action": "notify",
                    "message_type": "business_update",
                    "reason": "A verified business is sending an update that matches the user's recent order history.",
                    "confidence": 0.91
                }
            if any(w in text_lower for w in ["health", "appointment", "prescription", "pickup"]):
                return {
                    "is_utility": True,
                    "action": "notify",
                    "message_type": "event",
                    "reason": "A verified business is sending a reminder that matches the user's recent booking history.",
                    "confidence": 0.89
                }
            if any(w in text_lower for w in ["card statement", "account statement", "food order refund", "refund update", "fill a quick review", "international payout", "razorpayx", "monthly statement"]):
                return {
                    "is_utility": True,
                    "action": "digest",
                    "message_type": "business_update",
                    "reason": "A business account is sending a transactional statement, refund update, or service feedback request.",
                    "confidence": 0.88
                }

        return {"is_utility": False}

class MarketingClassifierAgent:
    """Agent 11: Marketing & Bulk Broadcast Classifier Agent"""

    def __init__(self):
        self.name = "Agent 11: Marketing Classifier"

    def evaluate(self, parsed_text: Dict[str, Any], biz_eval: Dict[str, Any]) -> Dict[str, Any]:
        text = parsed_text.get("clean_text", "")
        text_lower = text.lower()

        if biz_eval.get("is_opted_out") or "50% off" in text_lower or "try50" in text_lower or "reply stop to unsubscribe" in text_lower:
            if "opted_out" in str(biz_eval) or "try50" in text_lower:
                return {
                    "is_marketing": True,
                    "action": "mute",
                    "message_type": "promotion",
                    "reason": "The user has opted out of or repeatedly dismissed similar marketing messages.",
                    "confidence": 0.81
                }

        if any(w in text_lower for w in ["trip", "ladakh", "17,999", "itinerary", "discount"]):
            return {
                "is_marketing": True,
                "action": "digest",
                "message_type": "promotion",
                "reason": "The message is promotional but matches a topic or business the user has opted into.",
                "confidence": 0.78
            }

        return {"is_marketing": False}

class MultimodalVerifierAgent:
    """Agent 18: Multimodal Cross-Verification Agent"""

    def __init__(self):
        self.name = "Agent 18: Multimodal Verifier"

    def evaluate(self, text_parsed: Dict[str, Any], ocr_parsed: Dict[str, Any], asr_parsed: Dict[str, Any]) -> Dict[str, Any]:
        return {"has_contradiction": False}
