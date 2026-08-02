"""
Layer 5: Parallel Worker Manager, Media File Inspection, LLM Reasoning & Reviewer Engine
"""

import csv
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, List

from agents import (
    TextNormalizerAgent, OCRVisionAgent, ASRAudioAgent, MultilingualSlangParserAgent,
    UserProfileAgent, GroupDynamicsAgent, BusinessRelationshipAgent,
    HistoricalEvidenceAgent, QuietHoursAgent, FatigueBalancerAgent,
    ThreatSecurityAgent, UrgencyClassifierAgent, UtilityClassifierAgent,
    MarketingClassifierAgent, MultimodalVerifierAgent,
    DecisionArbiterAgent, SchemaValidatorAgent,
    FallbackResilienceAgent, LLMComplexReasonerAgent, ReviewerOrchestrator,
    QuickReplyGeneratorAgent, SLAMonitorEscalationAgent, DocumentMalwareInspectorAgent,
    PIIMinimizationAgent, PrivacyComplianceAgent
)

class DeduplicationCacheAgent:
    """Agent 15: Bounded Content Hashing & Deduplication Cache Agent"""

    def __init__(self, max_size: int = 1000):
        self.name = "Agent 15: Deduplication Cache"
        self.max_size = max_size
        self.cache: Dict[str, Dict[str, Any]] = {}

    def get_hash(self, text: str, media_id: str, user_id: str = "") -> str:
        content = f"{user_id}_{text}_{media_id}".encode("utf-8")
        return hashlib.md5(content).hexdigest()

    def get(self, key: str) -> Dict[str, Any]:
        return self.cache.get(key)

    def set(self, key: str, val: Dict[str, Any]):
        if key in self.cache:
            del self.cache[key]
        elif len(self.cache) >= self.max_size:
            first_key = next(iter(self.cache))
            del self.cache[first_key]
        self.cache[key] = val

class MessageRouterPipeline:
    """Master Orchestration Pipeline managing all Agents + Media File Inspection + LLMs + Reviewers + Privacy Gates"""

    def __init__(self, dataset_dir: str = "dataset"):
        self.dataset_dir = dataset_dir

        # Initialize Ingestion & Media File Inspection Agents
        self.pii_agent = PIIMinimizationAgent()
        self.text_agent = TextNormalizerAgent()
        self.slang_agent = MultilingualSlangParserAgent()
        self.ocr_agent = OCRVisionAgent(
            images_csv=f"{dataset_dir}/images.csv",
            base_dir=dataset_dir
        )
        self.asr_agent = ASRAudioAgent(
            voice_csv=f"{dataset_dir}/voice_notes.csv",
            base_dir=dataset_dir
        )

        # Context & Retrieval Agents
        self.user_agent = UserProfileAgent(users_file=f"{dataset_dir}/users.csv")
        self.group_agent = GroupDynamicsAgent(
            groups_file=f"{dataset_dir}/groups.csv",
            members_file=f"{dataset_dir}/group_members.csv"
        )
        self.biz_agent = BusinessRelationshipAgent(
            biz_file=f"{dataset_dir}/business_accounts.csv",
            history_file=f"{dataset_dir}/user_business_history.csv"
        )
        self.evidence_agent = HistoricalEvidenceAgent(
            history_file=f"{dataset_dir}/message_history.csv",
            events_file=f"{dataset_dir}/message_events.csv"
        )
        self.quiet_hours_agent = QuietHoursAgent()
        self.fatigue_agent = FatigueBalancerAgent(summary_file=f"{dataset_dir}/daily_notification_summary.csv")

        # Classifiers & Payload Security
        self.threat_agent = ThreatSecurityAgent()
        self.malware_agent = DocumentMalwareInspectorAgent()
        self.urgency_agent = UrgencyClassifierAgent()
        self.utility_agent = UtilityClassifierAgent()
        self.marketing_agent = MarketingClassifierAgent()
        self.multimodal_verifier_agent = MultimodalVerifierAgent()

        # Advanced Upgrades: SLA, Quick Replies & Privacy Compliance Gate
        self.sla_agent = SLAMonitorEscalationAgent()
        self.quick_reply_agent = QuickReplyGeneratorAgent()
        self.privacy_agent = PrivacyComplianceAgent()

        # LLM & Reviewer Mini-Agents
        self.llm_reasoner = LLMComplexReasonerAgent()
        self.reviewer_orchestrator = ReviewerOrchestrator()

        # Arbitration & QA
        self.arbiter_agent = DecisionArbiterAgent()
        self.schema_agent = SchemaValidatorAgent()
        self.fallback_agent = FallbackResilienceAgent()

        self.cache_agent = DeduplicationCacheAgent(max_size=1000)

    def process_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        msg_id = row.get("message_id", "")
        user_id = row.get("user_id", "")
        sender_id = row.get("sender_user_id", "")
        group_id = row.get("group_id", "")
        business_id = row.get("business_id", "")
        media_id = row.get("media_id", "")
        media_type = row.get("media_type", "")
        text = row.get("message_text", "")
        forwarded_count = int(row.get("forwarded_count") or 0)

        # Check Cache
        cache_key = self.cache_agent.get_hash(text, media_id, user_id)
        cached = self.cache_agent.get(cache_key)
        if cached:
            res = dict(cached)
            res["message_id"] = msg_id
            return res

        try:
            # Stage 0: Attachment Malware Inspection
            malware_res = self.malware_agent.inspect_attachment(media_id, text)
            if malware_res.get("is_malicious"):
                decision = {
                    "message_id": msg_id,
                    "action": malware_res["action"],
                    "message_type": malware_res["message_type"],
                    "reason": malware_res["reason"],
                    "confidence": malware_res["confidence"],
                    "evidence_message_ids": "none"
                }
                self.cache_agent.set(cache_key, decision)
                return decision

            # Stage 1: Preprocessing, Hinglish/Slang Parsing, Media Inspection & PII Redaction
            parsed_text = self.text_agent.process(text)
            parsed_text = self.pii_agent.minimize_parsed(parsed_text)

            slang_res = self.slang_agent.parse_intent(text)
            ocr_res = self.ocr_agent.process(media_id) if media_type == "image" else {}
            asr_res = self.asr_agent.process(media_id) if media_type == "voice" else {}
            sanitized_media = self.pii_agent.sanitize_transcripts(ocr_res, asr_res)

            # Stage 2: Context Retrieval
            user_profile = self.user_agent.get_user_info(user_id)
            user_profile = self.privacy_agent.sanitize_sensitive_attributes(user_profile)

            group_eval = self.group_agent.evaluate(user_id, group_id, sender_id)
            biz_eval = self.biz_agent.evaluate(user_id, business_id)

            evidence_eval = self.evidence_agent.find_evidence(user_id, sender_id, business_id, text)
            filtered_ev = self.privacy_agent.filter_cross_user_evidence(user_id, evidence_eval.get("evidence_message_ids", "none"), self.evidence_agent)
            evidence_eval["evidence_message_ids"] = filtered_ev

            user_load = self.fatigue_agent.get_user_load(user_id)

            # Stage 3: LLM Complex Reasoning (if API key present in env)
            llm_decision = self.llm_reasoner.analyze_with_llm(
                row, user_profile, group_eval, biz_eval,
                sanitized_media["ocr"].get("extracted_text", ""),
                sanitized_media["asr"].get("transcription", ""),
                filtered_ev
            )

            if llm_decision:
                decision = llm_decision
            else:
                # Local Multi-Agent Domain Classification
                threat_eval = self.threat_agent.evaluate(parsed_text, forwarded_count, group_eval, biz_eval)
                urgency_eval = self.urgency_agent.evaluate(parsed_text, group_eval, user_load)
                utility_eval = self.utility_agent.evaluate(parsed_text, biz_eval)
                marketing_eval = self.marketing_agent.evaluate(parsed_text, biz_eval)

                decision = self.arbiter_agent.arbitrate(
                    row, threat_eval, urgency_eval, utility_eval, marketing_eval, evidence_eval, llm_decision
                )

            # Stage 4: Reviewer Mini-Agents Audit & SLA Escalation
            reviewed_decision = self.reviewer_orchestrator.review_and_correct(row, group_eval, decision)
            sla_decision = self.sla_agent.evaluate_escalation(reviewed_decision)

            # Stage 5: Schema Validation
            validated = self.schema_agent.validate(sla_decision)

            # Stage 6: Privacy Compliance & Consent Hard-Stop Gate
            gated = self.privacy_agent.enforce_consent_hard_stop(validated, biz_eval)
            gated["evidence_message_ids"] = self.privacy_agent.filter_cross_user_evidence(user_id, gated.get("evidence_message_ids", "none"), self.evidence_agent)

            # Generate Smart Quick Replies for Extended Output
            quick_replies = self.quick_reply_agent.generate_actions(text, gated["action"], gated["message_type"])
            gated["quick_replies"] = quick_replies

            # Apply lower confidence marking for media-only fallback rows
            if not text.strip() and media_type:
                gated["confidence"] = 0.50
                gated["reason"] = f"Processed via metadata fallback inspection for {media_type} attachment."

            # Filter fields for output.csv contract compliance
            output_contract = {
                "message_id": gated["message_id"],
                "action": gated["action"],
                "message_type": gated["message_type"],
                "reason": gated["reason"],
                "confidence": gated["confidence"],
                "evidence_message_ids": gated["evidence_message_ids"]
            }

            # Store in cache
            self.cache_agent.set(cache_key, output_contract)

            return output_contract

        except Exception as e:
            return self.fallback_agent.handle_exception(msg_id, e)

    def process_dataset(self, input_csv: str, output_csv: str, num_workers: int = 8):
        rows = []
        with open(input_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)

        results = []
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            future_to_row = {executor.submit(self.process_row, row): i for i, row in enumerate(rows)}
            temp_results = [None] * len(rows)

            for future in as_completed(future_to_row):
                idx = future_to_row[future]
                temp_results[idx] = future.result()

            results = temp_results

        # Write output.csv
        fieldnames = ["message_id", "action", "message_type", "reason", "confidence", "evidence_message_ids"]
        with open(output_csv, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in results:
                writer.writerow(r)

        return len(results)

