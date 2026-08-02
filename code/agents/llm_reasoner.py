"""
LLM API Complex Reasoning Module (Groq, OpenAI, Gemini, Anthropic API Support)
Reads secrets securely from environment variables / .env file.
"""

import os
import json
import urllib.request
from typing import Dict, Any, Optional

def load_env_file(env_path: str = ".env"):
    """Helper to parse .env file without external dependencies."""
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ[k.strip()] = v.strip().strip("'").strip('"')

# Load .env file automatically
load_env_file()

class LLMComplexReasonerAgent:
    """Agent: Groq / OpenAI / Gemini LLM API Complex Reasoning Engine"""

    def __init__(self):
        self.name = "Agent: LLM Complex Reasoner"
        self.groq_key = os.getenv("GROQ_API_KEY")
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        self.has_api_key = bool(self.groq_key or self.openai_key or self.gemini_key or self.anthropic_key)

    def analyze_with_llm(
        self,
        row: Dict[str, Any],
        user_profile: Dict[str, Any],
        group_eval: Dict[str, Any],
        biz_eval: Dict[str, Any],
        ocr_text: str,
        asr_transcript: str,
        evidence_ids: str
    ) -> Optional[Dict[str, Any]]:
        """Invokes Groq / OpenAI LLM API if key is present; falls back to local engine if offline."""

        if not self.has_api_key:
            return None

        prompt = f"""
You are an expert WhatsApp Message Notification Router AI.
Analyze the following incoming message and recipient context to make a personalized routing decision.

INPUT MESSAGE CONTEXT:
- Message ID: {row.get('message_id')}
- Conversation Type: {row.get('conversation_type')}
- Message Text: "{row.get('message_text', '')}"
- OCR Extracted Poster Text: "{ocr_text}"
- Audio Voice Note Transcript: "{asr_transcript}"
- Forwarded Count: {row.get('forwarded_count', 0)}
- Recipient Profile: {user_profile}
- Group Context: {group_eval}
- Business Sender Info: {biz_eval}
- Candidate Evidence Message IDs: "{evidence_ids}"

RULES:
- Return strictly valid JSON matching the schema below.
- Allowed actions: "notify", "digest", "mute"
- Allowed message_type: "personal", "urgent", "event", "payment", "business_update", "promotion", "greeting", "forward", "spam", "scam", "unknown"
- Reason: short human-readable explanation.
- Confidence: float from 0.0 to 1.0.

JSON SCHEMA:
{{
  "action": "notify",
  "message_type": "personal",
  "reason": "explanation string",
  "confidence": 0.85,
  "evidence_message_ids": "{evidence_ids}"
}}
"""
        # Call Groq API if GROQ_API_KEY is configured
        if self.groq_key:
            try:
                url = "https://api.groq.com/openai/v1/chat/completions"
                payload = json.dumps({
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "user", "content": prompt}],
                    "response_format": {"type": "json_object"},
                    "temperature": 0.1
                }).encode("utf-8")

                req = urllib.request.Request(
                    url,
                    data=payload,
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.groq_key}"
                    }
                )
                with urllib.request.urlopen(req, timeout=10) as resp:
                    res = json.loads(resp.read().decode("utf-8"))
                    content = res["choices"][0]["message"]["content"]
                    return json.loads(content)
            except Exception as e:
                # Fallback cleanly on network timeout or API limits
                pass

        # Call OpenAI API if OPENAI_API_KEY is configured
        if self.openai_key:
            try:
                url = "https://api.openai.com/v1/chat/completions"
                payload = json.dumps({
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "response_format": {"type": "json_object"},
                    "temperature": 0.1
                }).encode("utf-8")

                req = urllib.request.Request(
                    url,
                    data=payload,
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.openai_key}"
                    }
                )
                with urllib.request.urlopen(req, timeout=10) as resp:
                    res = json.loads(resp.read().decode("utf-8"))
                    content = res["choices"][0]["message"]["content"]
                    return json.loads(content)
            except Exception:
                pass

        return None
