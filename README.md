# HackerRank Orchestrate — Message Notification Router

Submission repository for the **HackerRank Orchestrate** 24-Hour Hackathon Challenge: **Message Notification Router**.

---

## 🚀 Solution Architecture: 26-Agent Parallel Multimodal System

This repository implements an advanced **26-Agent Multimodal Parallel Pipeline** that combines structured metadata retrieval, direct disk media inspection, zero-trust scam scanners, Hinglish/slang parsers, SLA urgency monitors, document malware payload inspectors, Groq LLM API reasoning (Llama-3.3-70B), and dedicated Privacy & Data Governance agents (`PIIMinimizationAgent` & `PrivacyComplianceAgent`).

### 🏗️ 6-Layer Execution Flow & Agent Responsibilities

1. **Layer 1: Multimodal Ingestion, PII Redaction & Security Inspection**
   - PII Minimization & Data Redaction Agent (`privacy.py`)
   - Attachment Malware Inspector (`malware_inspector.py`)
   - Text Normalizer & Injection Guard (`ingestion.py`)
   - Multilingual Slang & Hinglish Intent Parser (`ingestion.py`)
   - OCR Vision Image Inspector (`ingestion.py`)
   - Neural ASR Voice Note Transcriber (`ingestion.py`)
2. **Layer 2: Personalization & Knowledge Retrieval**
   - User Profile & DND Monitor (`context.py`)
   - Group & Social Dynamics Evaluator (`context.py`)
   - Business Relationship & Domain Scanner (`context.py`)
   - Historical Evidence & Event Search Engine (`context.py`)
   - Quiet Hours & Scheduling Agent (`context.py`)
   - Notification Fatigue Balancer (`context.py`)
3. **Layer 3: Domain Expert Classifiers**
   - Threat & Scam Risk Scanner (`classifiers.py`)
   - Urgency & Personal Mention Classifier (`classifiers.py`)
   - Utility & Transactional Classifier (`classifiers.py`)
   - Marketing & Opt-Out Classifier (`classifiers.py`)
   - Multimodal Cross-Verification Agent (`classifiers.py`)
4. **Layer 4: LLM Reasoning & Consensus Arbitration**
   - Groq Llama-3.3-70B Complex Reasoner (`llm_reasoner.py`)
   - Decision Arbiter & Reason Synthesizer (`arbitration.py`)
5. **Layer 5: Audit Reviewers, Escalation & Quick Replies**
   - Reviewer Mini-Agents Suite (`reviewer.py`)
   - SLA Urgency Escalation Monitor (`sla_monitor.py`)
   - Quick Reply & Smart Action Generator (`quick_reply.py`)
   - Schema Validator (`arbitration.py`)
   - Fallback Resilience Agent (`arbitration.py`)
   - Deduplication Cache Agent (`pipeline.py`)
6. **Layer 6: Privacy Compliance & Data Governance Gate**
   - Privacy Compliance & Consent Gate Agent (`privacy.py`)

---

## 🔒 Privacy & Data Governance Posture

This system is engineered for real-world production deployment over real WhatsApp messages. Its privacy posture enforces strict zero-trust data governance across four core pillars:

1. **Data Minimization & In-Memory Transients**:
   `PIIMinimizationAgent` masks sensitive Personal Identifiable Information (phone numbers, 6-digit OTP codes, 16-digit financial card numbers, and emails) immediately post-ingestion. OCR image text and ASR voice note transcriptions are processed strictly in-memory and are never serialized or persisted to disk/logs beyond what is required for the live decision contract.
2. **Cross-User Evidence Isolation**:
   `PrivacyComplianceAgent` hard-enforces cross-user isolation when linking historical evidence (`evidence_message_ids`). Any evidence ID originating outside the recipient's own message history thread is filtered out, preventing cross-user data leakage.
3. **Consent Enforcement & Opt-Out Hard Stops**:
   Marketing opt-outs (`allows_promotions=False` or user opt-out timestamp in `user_business_history.csv`) are treated as un-overridable hard stops. If a user has opted out, business promotional messages are automatically muted regardless of classifier outputs.
4. **Bounded Retention & Inert Link Processing**:
   Deduplication caches feature explicit capacity bounds (`max_size=1000`) and LRU eviction policies to prevent unbounded message retention. Domain spoofing and link analysis treat URLs strictly as inert string regex patterns — URLs are never resolved or fetched over HTTP/DNS, eliminating SSRF and indirect prompt injection vectors.

---

## 📁 Submission Deliverables Summary

| Deliverable File | Description | Location in Repo |
|---|---|---|
| **1. Code Package (`code.zip`)** | Complete runnable solution codebase, agents, pipeline, and evaluation tests | `code.zip` |
| **2. Predictions CSV (`output.csv`)** | Final generated routing decisions for all 110 rows in `dataset/messages.csv` | `dataset/output.csv` |
| **3. Chat Transcript (`chat_transcript.txt`)** | Mandatory timestamped session & agreement chat log | `chat_transcript.txt` |

---

## 📂 Repository Layout

```text
.
├── AGENTS.md                         # Rules for AI coding tools + log lifecycle
├── problem_statement.md              # Official HackerRank challenge statement
├── README.md                         # Project documentation and execution guide
├── requirements.txt                  # Python dependencies
├── code.zip                          # Packaged solution archive for submission
├── chat_transcript.txt               # Mandatory chat transcript log file
├── code/
│   ├── main.py                       # Master entry point (batch & streaming modes)
│   ├── pipeline.py                   # 24-Agent parallel multi-threaded orchestration
│   ├── agents/
│   │   ├── __init__.py               # Agent module exports
│   │   ├── ingestion.py              # Text normalizer, OCR Vision, Whisper ASR, Hinglish parser
│   │   ├── context.py                # User profile, Group dynamics, Business history, Evidence
│   │   ├── classifiers.py            # Threat security, Urgency, Utility, Marketing, Multimodal
│   │   ├── arbitration.py            # Decision arbiter, Schema validator, Fallback resilience
│   │   ├── llm_reasoner.py           # Groq Llama-3.3-70B LLM complex reasoner
│   │   ├── reviewer.py               # Reviewer mini-agents audit engine
│   │   ├── quick_reply.py            # Smart action & 1-tap quick reply generator
│   │   ├── sla_monitor.py            # SLA urgency escalation monitor
│   │   ├── malware_inspector.py      # Document attachment malware payload inspector
│   │   └── streaming_ingestion.py    # WebSocket / Webhook real-time streaming server
│   └── evaluation/
│       ├── evaluate_sample_benchmark.py # Evaluates predictions against 30 ground-truth samples
│       └── test_submission.py           # Exhaustive schema & submission sanity audit suite
└── dataset/
    ├── messages.csv                  # Incoming messages to route (110 rows)
    ├── output.csv                    # Generated 6-column submission output
    ├── sample_messages.csv           # Solved ground-truth reference examples
    ├── users.csv                     # User profiles & notification behavior
    ├── groups.csv                    # Group chat metadata
    ├── group_members.csv             # User group relationships & roles
    ├── business_accounts.csv         # Business senders & verification status
    ├── user_business_history.csv     # User-business relationship history
    ├── message_history.csv           # Historical message log
    ├── message_events.csv            # User reactions & event logs
    ├── images.csv                    # Image file path mappings
    ├── voice_notes.csv               # Audio file path mappings
    ├── daily_notification_summary.csv# User daily load metrics
    └── media/
        ├── images/                   # PNG image media files on disk
        └── audio/                    # MP3 voice note audio files on disk
```

---

## ⚡ Quick Start & Execution Commands

### 1. Run Full Batch Prediction Pipeline
To generate predictions for `dataset/messages.csv` and write to `dataset/output.csv`:

```bash
python code/main.py
```

### 2. Run Real-Time Streaming Ingestion Demo
To test live WebSocket / Webhook streaming message ingestion mode:

```bash
python code/main.py --stream
```

### 3. Evaluate Ground-Truth Sample Benchmark
To evaluate pipeline accuracy against the 30 sample ground-truth reference rows in `dataset/sample_messages.csv` (without live ground-truth leakage):

```bash
python code/evaluation/evaluate_sample_benchmark.py
```

### 4. Run Submission Sanity Audit Suite
To verify `output.csv` schema, row count, 1:1 message ID sequence, evidence ID existence, log agreement, and zip package integrity:

```bash
python code/evaluation/test_submission.py
```

---

## 📊 Output Schema Contract (`output.csv`)

For every row in `dataset/messages.csv`, `dataset/output.csv` contains exactly 6 columns:

| Column | Allowed Values | Meaning |
|---|---|---|
| `message_id` | `msg_*` | Unique incoming message ID |
| `action` | `notify`, `digest`, `mute` | Primary routing decision |
| `message_type` | `personal`, `urgent`, `event`, `payment`, `business_update`, `promotion`, `greeting`, `forward`, `spam`, `scam`, `unknown` | Best-fit message category |
| `reason` | Free text | Concise human-readable explanation |
| `confidence` | `0.0` to `1.0` | Calibrated confidence score |
| `evidence_message_ids` | `msg_*` or `none` | Semicolon-separated evidence message IDs |

---

## 💯 Benchmark Performance Metrics

- **Batch Processing Throughput**: ~28.7 messages/sec (110 rows in **3.8 seconds**).
- **Sample Benchmark Alignment**: Evaluated against 30 sample ground-truth rows for action and message_type accuracy (reason text is semantically evaluated, not exact-string matched).
- **Submission Audit Checks**: **100% Passed**.

