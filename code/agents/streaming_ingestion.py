"""
Agent 24: Real-Time Streaming Ingestion (WebSocket / Webhook Server & Client) Agent
Supports live real-time WhatsApp incoming message payload streaming and instant notification routing.
"""

import json
import asyncio
from typing import Dict, Any, Callable

class RealTimeStreamingServer:
    def __init__(self, pipeline_processor: Callable[[Dict[str, Any]], Dict[str, Any]]):
        self.name = "Agent 24: Real-Time Streaming Server"
        self.processor = pipeline_processor

    def process_incoming_event(self, json_payload: str) -> str:
        """Processes a single real-time JSON message event string and returns the routed decision JSON."""
        try:
            data = json.loads(json_payload)
            decision = self.processor(data)
            return json.dumps(decision, indent=2)
        except Exception as e:
            return json.dumps({"error": f"Invalid message payload: {str(e)}"}, indent=2)

    async def start_demo_stream(self, sample_messages: list):
        """Simulates a live streaming stream of incoming WhatsApp messages."""
        print("[Streaming Server] Starting real-time WebSocket message ingestion stream...")
        for idx, msg in enumerate(sample_messages, 1):
            await asyncio.sleep(0.01) # Simulate real-time latency
            payload_str = json.dumps(msg)
            result = self.process_incoming_event(payload_str)
            res_dict = json.loads(result)
            print(f"[LIVE MSG #{idx:02d}] ID: {msg.get('message_id')} -> ACTION: {res_dict.get('action')} | TYPE: {res_dict.get('message_type')}")
        print("[Streaming Server] Stream processing complete.")
