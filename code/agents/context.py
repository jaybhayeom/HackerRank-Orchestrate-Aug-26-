"""
Layer 2: Personalization & Knowledge Retrieval Agents (Enhanced Relevance Matching & Full Dataset Utilization)
"""

import csv
import os
import re
from typing import Dict, Any, List, Optional

class UserProfileAgent:
    """Agent 5: User Profile & Behavior Agent"""

    def __init__(self, users_file: str = "dataset/users.csv"):
        self.name = "Agent 5: User Profile"
        self.users: Dict[str, Dict[str, Any]] = {}
        if os.path.exists(users_file):
            with open(users_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.users[row["user_id"]] = row

    def get_user_info(self, user_id: str) -> Dict[str, Any]:
        info = self.users.get(user_id, {})
        if not info:
            return {}
        return {
            "user_id": user_id,
            "do_not_disturb_window": info.get("do_not_disturb_window", "22:00-07:00"),
            "messages_opened_30d": int(info.get("messages_opened_30d") or 0),
            "messages_replied_30d": int(info.get("messages_replied_30d") or 0),
            "notifications_dismissed_30d": int(info.get("notifications_dismissed_30d") or 0),
            "messages_reported_30d": int(info.get("messages_reported_30d") or 0),
            "raw": info
        }

class GroupDynamicsAgent:
    """Agent 6: Group & Social Dynamics Agent"""

    def __init__(self, groups_file: str = "dataset/groups.csv", members_file: str = "dataset/group_members.csv"):
        self.name = "Agent 6: Group Dynamics"
        self.groups: Dict[str, Dict[str, Any]] = {}
        self.memberships: Dict[str, Dict[str, Any]] = {}

        if os.path.exists(groups_file):
            with open(groups_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.groups[row["group_id"]] = row

        if os.path.exists(members_file):
            with open(members_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    key = f"{row['user_id']}_{row['group_id']}"
                    self.memberships[key] = row

    def evaluate(self, user_id: str, group_id: str, sender_id: str) -> Dict[str, Any]:
        if not group_id:
            return {"is_group": False}

        group_info = self.groups.get(group_id, {})
        user_mem = self.memberships.get(f"{user_id}_{group_id}", {})
        sender_mem = self.memberships.get(f"{sender_id}_{group_id}", {})

        sender_is_admin = sender_mem.get("role") == "admin" or sender_mem.get("is_admin") == "true"
        user_group_muted = (
            user_mem.get("group_muted_by_user") in ["1", 1, "true"] or
            user_mem.get("is_muted") == "true" or
            user_mem.get("mute_status") == "muted"
        )

        return {
            "is_group": True,
            "group_name": group_info.get("group_name", ""),
            "group_type": group_info.get("group_type", "general"),
            "sender_is_admin": sender_is_admin,
            "user_group_muted": user_group_muted,
            "user_role": user_mem.get("role", "member"),
            "messages_sent_30d": int(user_mem.get("messages_sent_30d") or 0),
            "messages_read_30d": int(user_mem.get("messages_read_30d") or 0),
            "replies_sent_30d": int(user_mem.get("replies_sent_30d") or 0)
        }

class BusinessRelationshipAgent:
    """Agent 7: Business Relationship Agent"""

    def __init__(self, biz_file: str = "dataset/business_accounts.csv", history_file: str = "dataset/user_business_history.csv"):
        self.name = "Agent 7: Business Relationship"
        self.businesses: Dict[str, Dict[str, Any]] = {}
        self.history: Dict[str, List[Dict[str, Any]]] = {}

        if os.path.exists(biz_file):
            with open(biz_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.businesses[row["business_id"]] = row

        if os.path.exists(history_file):
            with open(history_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    u_id = row["user_id"]
                    if u_id not in self.history:
                        self.history[u_id] = []
                    self.history[u_id].append(row)

    def evaluate(self, user_id: str, business_id: str) -> Dict[str, Any]:
        if not business_id:
            return {"is_business": False}

        biz_info = self.businesses.get(business_id, {})
        user_biz_rel = [h for h in self.history.get(user_id, []) if h.get("business_id") == business_id]

        is_verified = biz_info.get("verified") in ["1", 1, "true"] or biz_info.get("is_verified") == "true"
        official_domain = biz_info.get("official_domain", "")
        sender_domain = biz_info.get("domain_used_by_sender", "")
        is_domain_spoofed = bool(official_domain and sender_domain and official_domain != sender_domain)

        user_reports = int(biz_info.get("user_reports_30d") or 0)
        domain_age = int(biz_info.get("domain_used_by_sender_age_days") or 9999)

        # Evaluate user activity with this business
        allows_promotions = any(r.get("allows_promotions") in ["1", 1, "true"] for r in user_biz_rel) if user_biz_rel else False
        is_opted_out = any(
            r.get("allows_promotions") in ["0", 0, "false"] or bool(r.get("promotions_opted_out_at"))
            for r in user_biz_rel
        ) if user_biz_rel else False

        why_knows = [r.get("why_user_knows_account", "") for r in user_biz_rel if r.get("why_user_knows_account")]
        has_recent_order = any("delivery" in w or "order" in w or "booking" in w or "payment" in w for w in why_knows)

        return {
            "is_business": True,
            "business_name": biz_info.get("display_name") or biz_info.get("brand_name", ""),
            "category": biz_info.get("category", ""),
            "is_verified": is_verified,
            "is_domain_spoofed": is_domain_spoofed,
            "user_reports_30d": user_reports,
            "domain_age_days": domain_age,
            "has_recent_order": has_recent_order,
            "allows_promotions": allows_promotions,
            "is_opted_out": is_opted_out,
            "why_user_knows_account": "; ".join(why_knows)
        }

class HistoricalEvidenceAgent:
    """Agent 8: Historical Evidence Search Agent (Semantic, Topic & Event Matching)"""

    def __init__(self, history_file: str = "dataset/message_history.csv", events_file: str = "dataset/message_events.csv"):
        self.name = "Agent 8: Historical Evidence Search"
        self.history: List[Dict[str, Any]] = []
        self.events: Dict[str, Dict[str, Any]] = {}

        if os.path.exists(events_file):
            with open(events_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.events[row.get("message_id", "")] = row

        self.history_by_id: Dict[str, Dict[str, Any]] = {}

        if os.path.exists(history_file):
            with open(history_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.history.append(row)
                    if row.get("message_id"):
                        self.history_by_id[row["message_id"]] = row

    def find_evidence(self, user_id: str, sender_id: str, business_id: str, text: str) -> Dict[str, Any]:
        text_words = set(re.findall(r"\w+", (text or "").lower()))
        matched_ids = []

        for msg in self.history:
            if msg.get("user_id") == user_id:
                msg_id = msg.get("message_id")
                # Match sender or business
                sender_match = (sender_id and msg.get("sender_user_id") == sender_id)
                biz_match = (business_id and msg.get("business_id") == business_id)
                
                # Word overlap score
                hist_text = (msg.get("message_text") or "").lower()
                hist_words = set(re.findall(r"\w+", hist_text))
                overlap = len(text_words.intersection(hist_words))

                if sender_match or biz_match or overlap >= 3:
                    event_info = self.events.get(msg_id, {})
                    is_opened = event_info.get("message_opened") in ["1", 1]
                    is_replied = event_info.get("message_replied") in ["1", 1]
                    
                    # Boost score if user actively engaged with historical message
                    score = overlap + (2 if sender_match or biz_match else 0) + (1 if is_opened else 0) + (2 if is_replied else 0)
                    matched_ids.append((score, msg_id))

        # Sort by relevance overlap & engagement score
        matched_ids = [m for m in matched_ids if m[1]]
        matched_ids.sort(key=lambda x: x[0], reverse=True)

        top_ids = []
        if matched_ids:
            max_score = matched_ids[0][0]
            if max_score >= 3:
                top_ids.append(matched_ids[0][1])
                if len(matched_ids) >= 2 and matched_ids[1][0] >= max_score - 1:
                    top_ids.append(matched_ids[1][1])
            else:
                top_ids.append(matched_ids[0][1])

        evidence_str = ";".join(top_ids) if top_ids else "none"

        return {
            "evidence_message_ids": evidence_str,
            "has_evidence": bool(top_ids)
        }

class QuietHoursAgent:
    """Agent 16: Quiet Hours & Scheduling Agent"""

    def __init__(self):
        self.name = "Agent 16: Quiet Hours"

    def is_in_quiet_hours(self, created_at: str, user_profile: Dict[str, Any]) -> bool:
        if not created_at:
            return False
        try:
            hour = int(created_at.split(" ")[1].split(":")[0])
            dnd_window = user_profile.get("do_not_disturb_window", "22:00-07:00")
            
            # Parse start and end hour from window string like "22:00-07:00"
            start_hour, end_hour = 22, 7
            if "-" in dnd_window:
                parts = dnd_window.split("-")
                start_hour = int(parts[0].split(":")[0])
                end_hour = int(parts[1].split(":")[0])

            if start_hour > end_hour:  # Overnight window (e.g. 22:00 to 07:00)
                return hour >= start_hour or hour < end_hour
            else:  # Same-day window (e.g. 09:00 to 17:00)
                return start_hour <= hour < end_hour
        except Exception:
            return False

class FatigueBalancerAgent:
    """Agent 17: Notification Fatigue & Rate Limiter Agent"""

    def __init__(self, summary_file: str = "dataset/daily_notification_summary.csv"):
        self.name = "Agent 17: Notification Fatigue"
        self.daily_loads: Dict[str, int] = {}
        if os.path.exists(summary_file):
            with open(summary_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    u_id = row.get("user_id")
                    sent_count = int(row.get("notifications_sent") or row.get("notification_count") or 0)
                    if u_id:
                        self.daily_loads[u_id] = self.daily_loads.get(u_id, 0) + sent_count

    def get_user_load(self, user_id: str) -> int:
        return self.daily_loads.get(user_id, 0)

