"""
HackerRank Orchestrate (August 2026) - Message Notification Router
Main Entry Point Executing the 24-Agent Parallel Architecture Pipeline.
"""

import os
import sys
import time
import csv

# Ensure code/ directory is on Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pipeline import MessageRouterPipeline
from agents import RealTimeStreamingServer

def main():
    print("=" * 70)
    print(" HackerRank Orchestrate - 24-Agent Message Notification Router")
    print("=" * 70)

    dataset_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dataset"))
    input_csv = os.path.join(dataset_dir, "messages.csv")
    output_csv = os.path.join(dataset_dir, "output.csv")

    if not os.path.exists(input_csv):
        print(f"Error: Input file missing at {input_csv}")
        sys.exit(1)

    pipeline = MessageRouterPipeline(dataset_dir=dataset_dir)

    if "--stream" in sys.argv:
        import asyncio
        print("[+] Mode: Real-Time Streaming Ingestion (WebSocket / Webhook Demo)")
        server = RealTimeStreamingServer(pipeline_processor=pipeline.process_row)
        sample_rows = []
        with open(input_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            sample_rows = [next(reader) for _ in range(5)]
        asyncio.run(server.start_demo_stream(sample_rows))
        return

    print(f"[+] Loading Dataset from: {input_csv}")
    print(f"[+] Output Target: {output_csv}")

    start_time = time.time()
    
    # Run 24-agent parallel processing
    processed_count = pipeline.process_dataset(
        input_csv=input_csv,
        output_csv=output_csv,
        num_workers=8
    )

    elapsed = time.time() - start_time

    print("-" * 70)
    print(f"[SUCCESS] Processed {processed_count} messages in {elapsed:.3f} seconds.")
    print(f"[+] Throughput: {processed_count / max(elapsed, 0.001):.1f} messages/sec.")

    # Sanity Check Output Validation
    if os.path.exists(output_csv):
        with open(output_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            rows = list(reader)
            print(f"[+] Output Columns: {fieldnames}")
            print(f"[+] Output Row Count: {len(rows)}")

            required_cols = ["message_id", "action", "message_type", "reason", "confidence", "evidence_message_ids"]
            if fieldnames == required_cols and len(rows) == processed_count:
                print("[+] VALIDATION PASSED: Output schema matches dataset contract perfectly!")
            else:
                print("[!] VALIDATION WARNING: Column headers or row count mismatch!")
    print("=" * 70)

if __name__ == "__main__":
    main()

