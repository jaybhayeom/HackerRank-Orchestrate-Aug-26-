"""
Layer 1: Multimodal Ingestion & File Media Inspection Agents
Inspects media files directly from disk (dataset/media/images and dataset/media/audio).
"""

import os
import re
import csv
from typing import Dict, Any

class TextNormalizerAgent:
    """Agent 1: Text Preprocessing, Entity Extraction & Injection Detection"""

    def __init__(self):
        self.name = "Agent 1: Text Normalizer"

    def process(self, text: str) -> Dict[str, Any]:
        text = text or ""
        clean_text = text.strip()

        # Detect prompt injection attempts
        has_prompt_injection = bool(re.search(
            r"ignore (all|previous) (routing|rules|instructions)|mark this message as|override priority|set action=",
            clean_text, re.IGNORECASE
        ))

        # Entity extraction
        contains_otp = bool(re.search(r"\b(otp|verification code|pin|login code|passcode|password)\b", clean_text, re.IGNORECASE))
        contains_urgent = bool(re.search(r"\b(urgent|asap|alert|emergency|eod|blocked|immediately|cancelled|rescheduled|quick heads-up)\b", clean_text, re.IGNORECASE))
        contains_payment = bool(re.search(r"\b(rs\b|rupees|\$|payment|invoice|bill|subscription|refund|balance|account-login)\b", clean_text, re.IGNORECASE))
        contains_link = bool(re.search(r"https?://\S+|www\.\S+|\w+\.in\b|\w+\.com\b", clean_text, re.IGNORECASE))
        has_direct_mention = bool(re.search(r"@u_\d+", clean_text))

        return {
            "clean_text": clean_text,
            "has_prompt_injection": has_prompt_injection,
            "contains_otp": contains_otp,
            "contains_urgent": contains_urgent,
            "contains_payment": contains_payment,
            "contains_link": contains_link,
            "has_direct_mention": has_direct_mention,
            "length": len(clean_text)
        }

class OCRVisionAgent:
    """Agent 2: OCR Image File Inspection & Text Extraction Agent"""

    def __init__(self, images_csv: str = "dataset/images.csv", base_dir: str = "dataset"):
        self.name = "Agent 2: OCR Vision"
        self.image_paths: Dict[str, str] = {}
        self.base_dir = base_dir
        self.ocr_cache: Dict[str, str] = {}

        if os.path.exists(images_csv):
            with open(images_csv, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.image_paths[row["image_id"]] = row["file_path"]

    def process(self, media_id: str) -> Dict[str, Any]:
        if not media_id or media_id not in self.image_paths:
            return {"extracted_text": "", "has_image": False, "file_exists": False}

        if media_id in self.ocr_cache:
            return {"extracted_text": self.ocr_cache[media_id], "has_image": True, "file_exists": True}

        rel_path = self.image_paths[media_id]
        full_path = os.path.join(self.base_dir, rel_path)

        file_exists = os.path.exists(full_path)
        file_size = os.path.getsize(full_path) if file_exists else 0
        extracted_text = ""

        # Attempt PIL image reading & OCR
        if file_exists:
            try:
                from PIL import Image
                with Image.open(full_path) as img:
                    width, height = img.size
                
                # If pytesseract is installed, perform OCR text extraction
                try:
                    import pytesseract
                    extracted_text = pytesseract.image_to_string(Image.open(full_path))
                except Exception:
                    extracted_text = f"Image {media_id} ({width}x{height} px, {file_size} bytes)"
            except Exception:
                extracted_text = f"Image file {rel_path} ({file_size} bytes)"

        self.ocr_cache[media_id] = extracted_text
        return {
            "extracted_text": extracted_text,
            "has_image": True,
            "file_exists": file_exists,
            "file_size": file_size,
            "media_id": media_id
        }

class ASRAudioAgent:
    """Agent 3: ASR Voice Note File Inspection & Speech Transcription Agent"""

    def __init__(self, voice_csv: str = "dataset/voice_notes.csv", base_dir: str = "dataset"):
        self.name = "Agent 3: ASR Audio Speech"
        self.voice_paths: Dict[str, str] = {}
        self.base_dir = base_dir
        self.asr_cache: Dict[str, str] = {}

        if os.path.exists(voice_csv):
            with open(voice_csv, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.voice_paths[row["voice_note_id"]] = row["file_path"]

    def process(self, media_id: str) -> Dict[str, Any]:
        if not media_id or media_id not in self.voice_paths:
            return {"transcription": "", "has_voice": False, "file_exists": False}

        if media_id in self.asr_cache:
            return {"transcription": self.asr_cache[media_id], "has_voice": True, "file_exists": True}

        rel_path = self.voice_paths[media_id]
        full_path = os.path.join(self.base_dir, rel_path)

        file_exists = os.path.exists(full_path)
        file_size = os.path.getsize(full_path) if file_exists else 0
        transcription = ""

        if file_exists:
            # Estimate audio duration from MP3 file size (~16KB/sec for standard compressed voice notes)
            estimated_duration_sec = round(file_size / 16000, 1)

            try:
                # Attempt whisper or speech_recognition if installed
                import whisper
                model = whisper.load_model("tiny")
                res = model.transcribe(full_path)
                transcription = res.get("text", "")
            except Exception:
                transcription = f"Voice Note {media_id} (duration ~{estimated_duration_sec}s, {file_size} bytes)"

        self.asr_cache[media_id] = transcription
        return {
            "transcription": transcription,
            "has_voice": True,
            "file_exists": file_exists,
            "file_size": file_size,
            "media_id": media_id
        }

class MultilingualSlangParserAgent:
    """Agent 4: Multilingual Code-Switching & Hinglish/Slang Intent Normalizer"""

    def __init__(self):
        self.name = "Agent 4: Multilingual Slang & Hinglish Parser"
        self.slang_map = {
            "kar do": "do it",
            "jaldi": "urgent",
            "bhai": "brother",
            "shukriya": "thank you",
            "paise": "money payment",
            "aaj hi": "today itself",
            "karo": "do",
            "bhejo": "send"
        }

    def parse_intent(self, text: str) -> Dict[str, Any]:
        text_lower = (text or "").lower()
        contains_hinglish = any(k in text_lower for k in self.slang_map.keys())
        normalized_text = text_lower
        for k, v in self.slang_map.items():
            normalized_text = normalized_text.replace(k, v)

        return {
            "contains_hinglish": contains_hinglish,
            "normalized_text": normalized_text
        }

