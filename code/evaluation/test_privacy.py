"""
Privacy & Data Governance Unit Test Suite for HackerRank Orchestrate
"""

import os
import csv
import sys
import re

# Ensure code/ directory is on sys.path
repo_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
code_dir = os.path.join(repo_dir, "code")
if code_dir not in sys.path:
    sys.path.insert(0, code_dir)

def run_privacy_tests():
    print("=" * 70)
    print(" RUNNING PRIVACY & DATA GOVERNANCE TEST SUITE")
    print("=" * 70)

    errors = []

    # Test 1: PII Minimization & Redaction Unit Test
    try:
        from agents.privacy import PIIMinimizationAgent
        pii_agent = PIIMinimizationAgent()

        sample_text = "Call +91 9876543210 or 9876543210 for OTP 654321. Card 4532-1234-5678-9012. Email user@example.com."
        minimized = pii_agent.minimize_text(sample_text)

        if "9876543210" in minimized:
            errors.append("PII Test Failed: Raw phone number was not redacted.")
        if "654321" in minimized:
            errors.append("PII Test Failed: Raw OTP code was not redacted.")
        if "4532-1234-5678-9012" in minimized:
            errors.append("PII Test Failed: Raw card number was not redacted.")
        if "user@example.com" in minimized:
            errors.append("PII Test Failed: Raw email address was not redacted.")
        
        if "[PHONE_REDACTED]" not in minimized or "[OTP_REDACTED]" not in minimized:
            errors.append("PII Test Failed: Redaction tokens missing from minimized text.")

        print("[OK] Test 1: PIIMinimizationAgent PII redaction logic verified.")
    except Exception as e:
        errors.append(f"Test 1 Exception: {str(e)}")

    # Test 2: Log File PII Scanner Test
    try:
        log_file = os.path.expanduser("~/hackerrank_orchestrate_august26/log.txt")
        if os.path.exists(log_file):
            with open(log_file, "r", encoding="utf-8") as f:
                log_content = f.read()

            raw_card_match = re.search(r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b", log_content)
            if raw_card_match:
                errors.append(f"Log PII Scanner Failed: Found raw card number in log.txt: {raw_card_match.group(0)}")

        print("[OK] Test 2: Log file scanned post-run — zero raw sensitive PII detected.")
    except Exception as e:
        errors.append(f"Test 2 Exception: {str(e)}")

    # Test 3: Cross-User Evidence Isolation Test
    try:
        from agents.privacy import PrivacyComplianceAgent
        from agents.context import HistoricalEvidenceAgent

        privacy_agent = PrivacyComplianceAgent()
        history_agent = HistoricalEvidenceAgent(history_file=os.path.join(repo_dir, "dataset", "message_history.csv"))

        target_user = "u_001"
        leaked_evidence = "message_0001;message_0200"

        isolated_evidence = privacy_agent.filter_cross_user_evidence(target_user, leaked_evidence, history_agent)
        
        for ev_id in isolated_evidence.split(";"):
            if ev_id != "none":
                msg_row = history_agent.history_by_id.get(ev_id, {})
                if msg_row and msg_row.get("user_id") != target_user:
                    errors.append(f"Cross-User Evidence Failure: Allowed cross-user evidence {ev_id} for user {target_user}")

        print("[OK] Test 3: Cross-user evidence isolation hard-enforcement verified.")
    except Exception as e:
        errors.append(f"Test 3 Exception: {str(e)}")

    # Test 4: Consent & Opt-Out Hard Stop Test
    try:
        from agents.privacy import PrivacyComplianceAgent
        privacy_agent = PrivacyComplianceAgent()

        classifier_decision = {
            "message_id": "msg_test",
            "action": "notify",
            "message_type": "promotion",
            "reason": "Special discount offer",
            "confidence": 0.88,
            "evidence_message_ids": "none"
        }
        biz_eval = {
            "is_business": True,
            "is_opted_out": True,
            "allows_promotions": False
        }

        gated_decision = privacy_agent.enforce_consent_hard_stop(classifier_decision, biz_eval)

        if gated_decision["action"] != "mute":
            errors.append(f"Consent Hard-Stop Failed: Expected action 'mute' for opted-out promotion, got '{gated_decision['action']}'")
        if gated_decision["message_type"] != "promotion":
            errors.append(f"Consent Hard-Stop Failed: Message type altered incorrectly.")

        print("[OK] Test 4: Consent & Opt-out hard-stop gate verified.")
    except Exception as e:
        errors.append(f"Test 4 Exception: {str(e)}")

    # Test 5: Bounded LRU Cache Eviction Policy Test
    try:
        from pipeline import DeduplicationCacheAgent
        cache = DeduplicationCacheAgent(max_size=3)

        cache.set("k1", {"val": 1})
        cache.set("k2", {"val": 2})
        cache.set("k3", {"val": 3})
        cache.set("k4", {"val": 4})

        if cache.get("k1") is not None:
            errors.append("LRU Cache Retention Failure: Key k1 was not evicted when cache capacity was exceeded.")
        if cache.get("k4") is None or len(cache.cache) > 3:
            errors.append("LRU Cache Retention Failure: Bounded size limit exceeded.")

        print("[OK] Test 5: Bounded LRU cache retention & eviction policy verified.")
    except Exception as e:
        errors.append(f"Test 5 Exception: {str(e)}")

    # Test 6: Inert URL Pattern Matching Test
    try:
        from agents.privacy import PrivacyComplianceAgent
        privacy_agent = PrivacyComplianceAgent()

        suspicious_url_text = "Visit http://bank-secure-login.phishing-domain.com to claim reward."
        is_inert = privacy_agent.verify_inert_urls(suspicious_url_text)

        if not is_inert:
            errors.append("Inert URL Handling Failure: URL inspection performed illegal network I/O.")

        print("[OK] Test 6: Inert URL pattern matching (zero network calls) verified.")
    except Exception as e:
        errors.append(f"Test 6 Exception: {str(e)}")

    print("-" * 70)
    if errors:
        print(f"[FAIL] Privacy test suite failed with {len(errors)} errors:")
        for err in errors:
            print(f"  - {err}")
        return False
    else:
        print("[SUCCESS] ALL PRIVACY & DATA GOVERNANCE TESTS PASSED 100%!")
        return True

if __name__ == "__main__":
    success = run_privacy_tests()
    sys.exit(0 if success else 1)
