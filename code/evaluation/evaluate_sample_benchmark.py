"""
Evaluation & Benchmarking Script comparing predictions against dataset/sample_messages.csv
"""

import os
import sys
import csv

# Add code/ to path
repo_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(repo_dir, "code"))

from pipeline import MessageRouterPipeline

def run_sample_evaluation():
    print("=" * 70)
    print(" EVALUATING 20-AGENT PIPELINE ON dataset/sample_messages.csv BENCHMARK")
    print("=" * 70)

    dataset_dir = os.path.join(repo_dir, "dataset")
    sample_csv = os.path.join(dataset_dir, "sample_messages.csv")
    sample_output_csv = os.path.join(dataset_dir, "sample_predictions.csv")

    if not os.path.exists(sample_csv):
        print(f"Error: {sample_csv} missing!")
        return

    # Load Ground Truth Samples
    ground_truth = {}
    with open(sample_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            ground_truth[r["message_id"]] = r

    total_samples = len(ground_truth)
    print(f"[+] Loaded {total_samples} ground-truth sample benchmark rows.")

    # Initialize Pipeline
    pipeline = MessageRouterPipeline(dataset_dir=dataset_dir)
    
    # Process sample messages
    pipeline.process_dataset(
        input_csv=sample_csv,
        output_csv=sample_output_csv,
        num_workers=4
    )

    # Load Predictions
    predictions = {}
    with open(sample_output_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            predictions[r["message_id"]] = r

    # Compute Metrics
    action_matches = 0
    type_matches = 0
    reason_matches = 0
    evidence_matches = 0

    print("-" * 70)
    print(f"{'MSG ID':<16} | {'PRED ACTION':<10} | {'GT ACTION':<10} | {'PRED TYPE':<12} | {'GT TYPE':<12}")
    print("-" * 70)

    for msg_id, gt in ground_truth.items():
        pred = predictions.get(msg_id, {})
        pred_action = pred.get("action")
        gt_action = gt.get("action")

        pred_type = pred.get("message_type")
        gt_type = gt.get("message_type")

        pred_ev = set((pred.get("evidence_message_ids") or "none").split(";"))
        gt_ev = set((gt.get("evidence_message_ids") or "none").split(";"))

        if pred_action == gt_action:
            action_matches += 1
        if pred_type == gt_type:
            type_matches += 1
        if pred.get("reason", "").strip() == gt.get("reason", "").strip():
            reason_matches += 1
        if pred_ev == gt_ev:
            evidence_matches += 1

        status_action = "OK" if pred_action == gt_action else "MISMATCH"
        print(f"{msg_id:<16} | {str(pred_action):<10} | {str(gt_action):<10} | {str(pred_type):<12} | {str(gt_type):<12}")

    action_acc = (action_matches / total_samples) * 100
    type_acc = (type_matches / total_samples) * 100
    reason_acc = (reason_matches / total_samples) * 100
    evidence_acc = (evidence_matches / total_samples) * 100

    print("=" * 70)
    print(" BENCHMARK ACCURACY EVALUATION RESULTS")
    print("=" * 70)
    print(f" Action Classification Accuracy   : {action_acc:.2f}% ({action_matches}/{total_samples})")
    print(f" Message Type Accuracy           : {type_acc:.2f}% ({type_matches}/{total_samples})")
    print(f" Exact Reason Alignment Accuracy  : {reason_acc:.2f}% ({reason_matches}/{total_samples})")
    print(f" Evidence ID Match Rate           : {evidence_acc:.2f}% ({evidence_matches}/{total_samples})")
    print("=" * 70)

    if os.path.exists(sample_output_csv):
        os.remove(sample_output_csv)

if __name__ == "__main__":
    run_sample_evaluation()
