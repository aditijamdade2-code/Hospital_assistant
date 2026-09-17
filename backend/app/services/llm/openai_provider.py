import json
import logging
import httpx
from typing import Optional, List, Dict, Any
from backend.app.services.llm.base import LLMProvider, StructuredExtraction
from backend.app.services.llm.mock_provider import MockLocalLLMProvider
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

class OpenAIProvider(LLMProvider):
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or settings.OPENAI_MODEL
        self.base_url = (base_url or settings.OPENAI_BASE_URL).rstrip("/")
        self.fallback = MockLocalLLMProvider()

    async def extract_information(
        self,
        text: str,
        conversation_history: List[Dict[str, str]],
        current_language: str = "en"
    ) -> StructuredExtraction:
        if not self.api_key:
            logger.warning("OpenAI API key missing; falling back to MockLocalLLMProvider.")
            return await self.fallback.extract_information(text, conversation_history, current_language)

        system_prompt = (
            "You are a clinical intake assistant for a hospital OPD. "
            "Your task is strictly to understand patient natural language and extract structured JSON information. "
            "CRITICAL CLINICAL SAFETY RULES:\n"
            "1. Do NOT invent, assume, or hallucinate missing medical information.\n"
            "2. If a field is not explicitly mentioned or clearly implied by the patient, it MUST be set to null.\n"
            "3. Return ONLY valid JSON with keys: chief_complaint, body_part, symptoms (array), duration, severity, additional_fields (object), detected_language."
        )

        messages = [{"role": "system", "content": system_prompt}]
        for msg in conversation_history[-4:]:
            messages.append({"role": msg.get("sender", "user").lower(), "content": msg.get("content", "")})
        messages.append({"role": "user", "content": text})

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": 0.0,
                        **({"format": "json"} if "11434" in self.base_url or "ollama" in self.base_url else {"response_format": {"type": "json_object"}})
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    parsed = json.loads(content)
                    return StructuredExtraction(
                        chief_complaint=parsed.get("chief_complaint"),
                        body_part=parsed.get("body_part"),
                        symptoms=parsed.get("symptoms", []),
                        duration=parsed.get("duration"),
                        severity=parsed.get("severity"),
                        additional_fields=parsed.get("additional_fields", {}),
                        detected_language=parsed.get("detected_language", current_language)
                    )
                else:
                    logger.error(f"OpenAI API error {response.status_code}: {response.text}")
                    return await self.fallback.extract_information(text, conversation_history, current_language)
        except Exception as e:
            logger.error(f"OpenAI extraction call failed: {e}; falling back to local extractor.")
            return await self.fallback.extract_information(text, conversation_history, current_language)

    async def generate_response(
        self,
        patient_message: str,
        conversation_history: List[Dict[str, str]],
        next_question: Optional[str],
        guidance_steps: Optional[List[Dict[str, Any]]],
        alert_instruction: Optional[str],
        language: str = "en"
    ) -> str:
        # Emergency alerts must remain deterministic for safety
        if alert_instruction or not self.api_key:
            return await self.fallback.generate_response(
                patient_message,
                conversation_history,
                next_question,
                guidance_steps,
                alert_instruction,
                language
            )

        try:
            lang_name = "Marathi" if language == "mr" else "Hindi" if language == "hi" else "English"
            system_prompt = (
                f"You are a helpful, compassionate hospital OPD triage assistant replying in {lang_name}. "
                "Keep responses concise (1-2 sentences), empathetic, and professional. "
                "Do NOT give a medical diagnosis or prescribe medications. "
            )
            if next_question:
                system_prompt += f"Acknowledge the patient's input with empathy, then ask this clinical question in {lang_name}: '{next_question}'."
            elif guidance_steps:
                steps_txt = "\n".join([f"{s.get('step')}. {s.get('instruction')}" for s in guidance_steps])
                system_prompt += f"Briefly share these approved first-aid instructions in {lang_name}:\n{steps_txt}\nRemind them healthcare staff will see them shortly."
            else:
                system_prompt += f"In {lang_name}, politely acknowledge their confirmation, reassure them that their details are recorded for the doctors, and advise them to rest comfortably in the waiting area."

            messages = [{"role": "system", "content": system_prompt}]
            for msg in conversation_history[-3:]:
                sender_role = "assistant" if msg.get("sender") in ["ASSISTANT", "CLINICAL_STAFF"] else "user"
                messages.append({"role": sender_role, "content": msg.get("content", "")})
            messages.append({"role": "user", "content": patient_message})

            async with httpx.AsyncClient(timeout=12.0) as client:
                res = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": 0.3
                    }
                )
                if res.status_code == 200:
                    data = res.json()
                    reply = data["choices"][0]["message"]["content"].strip()
                    if reply:
                        return reply
        except Exception as e:
            logger.warning(f"LLM natural response generation failed: {e}; using deterministic fallback.")

        return await self.fallback.generate_response(
            patient_message,
            conversation_history,
            next_question,
            guidance_steps,
            alert_instruction,
            language
        )
