"""
Base Agent Module: Provides unified Gemini SDK integration, error handling,
prompt templates, and diagnostic telemetry.
"""

import json
import os
import re
import time
from typing import Any, Dict, Optional, Tuple


class BaseGeminiAgent:
    """Base class for all Gemini-powered agents in the debugging pipeline."""

    def __init__(
        self,
        name: str,
        role_description: str,
        api_key: Optional[str] = None,
        model_name: str = "gemini-3.5-flash",
    ):
        self.name = name
        self.role_description = role_description
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "").strip()
        self.model_name = model_name
        self._client = None
        self._legacy_model = None
        self._init_client()

    def _init_client(self):
        """Initializes Google GenAI client or legacy generativeai client."""
        if not self.api_key:
            return

        # Attempt 1: Modern google-genai SDK
        try:
            from google import genai
            self._client = genai.Client(api_key=self.api_key)
            return
        except Exception:
            self._client = None

        # Attempt 2: google.generativeai SDK
        try:
            import google.generativeai as genai_legacy
            genai_legacy.configure(api_key=self.api_key)
            # Map model name if needed
            legacy_model_name = self.model_name
            if "2.5" in legacy_model_name:
                legacy_model_name = "gemini-1.5-flash"
            self._legacy_model = genai_legacy.GenerativeModel(
                model_name=legacy_model_name,
                system_instruction=self.role_description
            )
        except Exception:
            self._legacy_model = None

    def call_gemini(
        self,
        user_prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.2,
    ) -> Tuple[str, float]:
        """
        Executes a prompt against Gemini API with latency measurement.
        Returns (response_text, latency_seconds).
        """
        start_time = time.perf_counter()
        effective_system = system_instruction or self.role_description

        # If API key is present and clients initialized
        if self._client:
            try:
                from google.genai import types
                response = self._client.models.generate_content(
                    model=self.model_name,
                    contents=user_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=effective_system,
                        temperature=temperature,
                    )
                )
                latency = time.perf_counter() - start_time
                return response.text or "", latency
            except Exception as e:
                # If modern client fails with model name issue, try fallback
                pass

        if self._legacy_model:
            try:
                response = self._legacy_model.generate_content(
                    user_prompt,
                    generation_config={"temperature": temperature}
                )
                latency = time.perf_counter() - start_time
                return response.text or "", latency
            except Exception as e:
                pass

        # If no API key or API call failed, raise RuntimeError to trigger fallback
        raise RuntimeError(
            f"Gemini API invocation failed or API key not provided for agent '{self.name}'."
        )

    def extract_json(self, text: str) -> Dict[str, Any]:
        """Extracts and parses JSON from model output with resilient fallbacks."""
        text = text.strip()
        # Look for markdown code fence
        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        if json_match:
            candidate = json_match.group(1).strip()
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                pass

        # Direct JSON decode
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Substring search for first { and last }
        start_idx = text.find("{")
        end_idx = text.rfind("}")
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            try:
                return json.loads(text[start_idx : end_idx + 1])
            except json.JSONDecodeError:
                pass

        return {"raw_content": text}
