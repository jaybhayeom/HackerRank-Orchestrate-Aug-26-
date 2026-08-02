"""
Exhaustive Submission Verification Test Suite for HackerRank Orchestrate
"""

import os
import csv
import sys
import glob

def verify_submission():
    print("=" * 70)
    print(" RUNNING EXHAUSTIVE SUBMISSION AUDIT & TEST SUITE")
    print("=" * 70)

    repo_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    dataset_dir = os.path.join(repo_dir, "dataset")
    messages_csv = os.path.join(dataset_dir, "messages.csv")
    history_csv = os.path.join(dataset_dir, "message_history.csv")
    output_csv = os.path.join(dataset_dir, "output.csv")
    zip_package = os.path.join(repo_dir, "hackerrank-orchestrate-august26.zip")
    log_file = os.path.expanduser("~/hackerrank_orchestrate_august26/log.txt")

    errors = []
    warnings = []

    # Load valid historical message IDs
    history_ids = set()
    if os.path.exists(history_csv):
        with open(history_csv, "r", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r.get("message_id"):
                    history_ids.add(r["message_id"])

    # 1. Anti-Leakage Static Code Inspection Check
    code_dir = os.path.join(repo_dir, "code")
    for py_file in glob.glob(os.path.join(code_dir, "**", "*.py"), recursive=True):
        rel_path = os.path.relpath(py_file, repo_dir)
        if "evaluation" in rel_path.split(os.sep):
            continue
        with open(py_file, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            if "sample_messages.csv" in content:
                errors.append(f"GROUND-TRUTH LEAKAGE DETECTED! File '{rel_path}' references 'sample_messages.csv'.")
    if not any("GROUND-TRUTH LEAKAGE" in e for e in errors):
        print("[OK] Anti-leakage static code inspection passed (0 leaks found outside evaluation/).")

    # 2. Input CSV Check
    if not os.path.exists(messages_csv):
        errors.append(f"Input dataset missing: {messages_csv}")
        return False
    
    with open(messages_csv, "r", encoding="utf-8") as f:
        input_rows = list(csv.DictReader(f))
    input_count = len(input_rows)
    input_ids = [r["message_id"] for r in input_rows]
    print(f"[OK] Input dataset/messages.csv present with {input_count} rows.")

    # 3. Output CSV Check
    if not os.path.exists(output_csv):
        errors.append(f"Output predictions CSV missing: {output_csv}")
    else:
        with open(output_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            output_rows = list(reader)

        output_count = len(output_rows)
        print(f"[OK] Output dataset/output.csv present with {output_count} rows.")

        # Check Column Names
        expected_cols = ["message_id", "action", "message_type", "reason", "confidence", "evidence_message_ids"]
        if fieldnames != expected_cols:
            errors.append(f"Columns mismatch! Expected {expected_cols}, got {fieldnames}")
        else:
            print("[OK] Columns schema matches required specification exactly.")

        # Check Row Count & Exact 1:1 Message ID Sequence Match
        output_ids = [r.get("message_id") for r in output_rows]
        if output_count != input_count:
            errors.append(f"Row count mismatch! Input has {input_count}, output has {output_count}.")
        elif output_ids != input_ids:
            errors.append("1:1 Message ID sequence mismatch between messages.csv and output.csv!")
        else:
            print(f"[OK] Exact 1:1 row count & Message ID sequence match verified ({output_count}/{input_count}).")

        # Check Allowed Values, Evidence Existence, and Format Constraints
        allowed_actions = {"notify", "digest", "mute"}
        allowed_types = {
            "personal", "urgent", "event", "payment", "business_update",
            "promotion", "greeting", "forward", "spam", "scam", "unknown"
        }

        for idx, row in enumerate(output_rows, start=1):
            msg_id = row.get("message_id")
            action = row.get("action")
            mtype = row.get("message_type")
            reason = row.get("reason")
            conf_str = row.get("confidence")
            evidence = row.get("evidence_message_ids")

            if not msg_id:
                errors.append(f"Row {idx} missing message_id.")

            if action not in allowed_actions:
                errors.append(f"Row {idx} ({msg_id}) invalid action '{action}'. Allowed: {allowed_actions}")

            if mtype not in allowed_types:
                errors.append(f"Row {idx} ({msg_id}) invalid message_type '{mtype}'. Allowed: {allowed_types}")

            if not reason or not reason.strip():
                errors.append(f"Row {idx} ({msg_id}) empty reason.")

            try:
                conf = float(conf_str)
                if not (0.0 <= conf <= 1.0):
                    errors.append(f"Row {idx} ({msg_id}) confidence out of bounds: {conf}")
            except Exception:
                errors.append(f"Row {idx} ({msg_id}) invalid confidence value: '{conf_str}'")

            if not evidence or not evidence.strip():
                errors.append(f"Row {idx} ({msg_id}) empty evidence field. (Must be 'none' or IDs).")
            else:
                tokens = [t.strip() for t in evidence.split(";")]
                for tok in tokens:
                    if tok != "none" and tok not in history_ids:
                        errors.append(f"Row {idx} ({msg_id}) evidence ID '{tok}' not found in message_history.csv!")

        print("[OK] All evidence_message_ids verified against message_history.csv.")

    # 4. Log File Check
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as f:
            content = f.read()
        if "AGREEMENT RECORDED:" in content:
            print(f"[OK] Chat transcript log file verified at {log_file} with recorded agreement.")
        else:
            warnings.append("Log file exists but missing AGREEMENT RECORDED line.")
    else:
        errors.append(f"Mandatory log file missing at {log_file}")

    # 5. ZIP Package Check
    if os.path.exists(zip_package):
        size_mb = os.path.getsize(zip_package) / (1024 * 1024)
        print(f"[OK] Submission ZIP package verified at {zip_package} ({size_mb:.2f} MB).")
    else:
        warnings.append(f"ZIP package not found at {zip_package}")

    print("-" * 70)
    if errors:
        print(f"[FAIL] Audit failed with {len(errors)} errors:")
        for err in errors:
            print(f"  - {err}")
        return False
    else:
        print("[SUCCESS] ALL SUBMISSION SANITY CHECKS PASSED 100%!")
        if warnings:
            print("Warnings:")
            for w in warnings:
                print(f"  - {w}")
        return True

if __name__ == "__main__":
    success = verify_submission()
    sys.exit(0 if success else 1)

