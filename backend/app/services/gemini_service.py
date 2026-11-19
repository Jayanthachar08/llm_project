import json
import logging
import re
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

from google import genai
from google.genai import types
from google.genai.errors import APIError

from backend.app.core.config import settings
from backend.app.schemas.gemini import GeminiExtractionResult, ExtractedTaskItem
from backend.app.services.prompt_service import prompt_service

logger = logging.getLogger("campusflow.gemini_service")

# Official CampusFlow AI System Prompt
SYSTEM_PROMPT = prompt_service.get_main_system_prompt() + "\n\n" + prompt_service.get_structured_json_schema_prompt()

class GeminiService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = settings.GEMINI_MODEL or "gemini-3.5-flash-lite"
        self._client: Optional[genai.Client] = None
        self._configured = False

        if self.api_key and self.api_key.strip() and self.api_key != "your_gemini_api_key_here":
            try:
                self._client = genai.Client(api_key=self.api_key.strip())
                self._configured = True
                logger.info("Modern Google GenAI SDK Client initialized with model: %s", self.model_name)
            except Exception as e:
                logger.error("Failed to initialize Google GenAI Client: %s", e)

    def is_configured(self) -> bool:
        return self._configured and self._client is not None

    def test_connection(self) -> Dict[str, Any]:
        """
        Actively verify model availability and API key connectivity through a live Gemini request.
        Returns connection diagnostics without masking errors.
        """
        if not self.is_configured():
            return {
                "configured": False,
                "connected": False,
                "model": self.model_name,
                "sdk": "google-genai",
                "error": "GEMINI_API_KEY is not set or set to placeholder in environment/.env file."
            }

        try:
            response = self._client.models.generate_content(
                model=self.model_name,
                contents="CampusFlow AI connection ping. Respond with 'PONG'."
            )
            return {
                "configured": True,
                "connected": True,
                "model": self.model_name,
                "sdk": "google-genai",
                "response": response.text.strip() if response.text else "OK",
                "error": None
            }
        except Exception as e:
            logger.error("Live Gemini connectivity check failed: %s", e)
            return {
                "configured": True,
                "connected": False,
                "model": self.model_name,
                "sdk": "google-genai",
                "error": str(e)
            }

    def extract_tasks_from_text(self, text: str, rag_context: Optional[str] = None) -> GeminiExtractionResult:
        """
        Extract structured academic tasks from raw announcement text using Google GenAI SDK.
        Primary LLM: Gemini 3.5 Flash-Lite (exact model identifier: gemini-3.5-flash-lite).
        Supports augmented retrieval context (RAG) when provided.
        Uses deterministic heuristic parser for offline test environments or when API key is unavailable.
        """
        current_date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d (%A)")
        
        full_prompt = prompt_service.get_announcement_extraction_prompt(
            announcement_text=text,
            current_date=current_date_str,
            rag_context=rag_context
        )

        if self.is_configured():
            try:
                response = self._client.models.generate_content(
                    model=self.model_name,
                    contents=full_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                        response_mime_type="application/json",
                        temperature=0.1
                    )
                )
                raw_json = response.text.strip()
                
                # Strip markdown code blocks if returned
                if raw_json.startswith("```"):
                    raw_json = re.sub(r"^```(?:json)?\n", "", raw_json)
                    raw_json = re.sub(r"\n```$", "", raw_json)

                parsed_data = json.loads(raw_json)
                parsed_data["model_used"] = self.model_name
                parsed_data["extraction_mode"] = "live_gemini"

                validated_result = GeminiExtractionResult.model_validate(parsed_data)
                logger.info("Successfully extracted %d tasks using live Gemini (%s)", len(validated_result.tasks), self.model_name)
                return validated_result
            except Exception as e:
                logger.error("Gemini GenAI SDK error: %s. Using heuristic fallback.", e)
                return self._fallback_extraction(text, f"Gemini GenAI API error: {str(e)}")
        else:
            logger.info("Gemini API key not configured. Running deterministic academic parser.")
            return self._fallback_extraction(text, "Local deterministic academic parser (configure GEMINI_API_KEY for live LLM extraction)")

    def generate_study_explanation(self, task_title: str, priority_score: float, deadline: Optional[str]) -> str:
        """Generate context-aware study recommendation via Gemini 3.5 Flash-Lite or deterministic fallback."""
        if self.is_configured():
            try:
                resp = self._client.models.generate_content(
                    model=self.model_name,
                    contents=prompt_service.get_study_recommendation_prompt(task_title, priority_score, deadline),
                    config=types.GenerateContentConfig(temperature=0.3)
                )
                return resp.text.strip()
            except Exception:
                pass
        return f"Focus on '{task_title}' early. Break the workload into focused 60-minute sessions before the target deadline."

    def _fallback_extraction(self, text: str, reason: str) -> GeminiExtractionResult:
        """Deterministic rule-based extractor to guarantee 100% test reliability and offline support."""
        tasks: List[ExtractedTaskItem] = []
        
        subjects = [
            "DBMS", "Database Management Systems",
            "CN", "Computer Networks",
            "AI", "Artificial Intelligence",
            "Operating Systems", "OS",
            "Python", "Machine Learning", "ML",
            "Cloud Computing", "Software Engineering", "Mathematics",
            "Graphics", "Computer Graphics"
        ]
        
        date_pattern = r"(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2}(?:st|nd|rd|th)?(?:\s*,?\s*\d{4})?|\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{2,4}"

        # Split text into sentences
        raw_sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", text) if s.strip()]
        
        # Group sentences into tasks: a sentence with academic activity/date starts a task,
        # auxiliary sentences (e.g. "Prepare all 5 modules") become instructions.
        task_blocks: List[str] = []
        for s in raw_sentences:
            is_new_activity = any(k in s.lower() for k in [
                "assignment", "exam", "test", "internal", "midterm", "quiz",
                "lab", "practical", "project", "symposium", "workshop", "hackathon",
                "due", "conducted on", "deadline", "scheduled on"
            ])
            if is_new_activity or not task_blocks:
                task_blocks.append(s)
            else:
                task_blocks[-1] += " " + s

        for p_clean in task_blocks:
            if len(p_clean) < 10:
                continue

            found_subject = None
            for subj in subjects:
                if re.search(rf"\b{re.escape(subj)}\b", p_clean, re.IGNORECASE):
                    found_subject = subj
                    break

            date_match = re.search(date_pattern, p_clean, re.IGNORECASE)
            extracted_date = None
            needs_verification = False
            verification_reason = None

            if date_match:
                extracted_date = date_match.group(0)
            elif any(w in p_clean.lower() for w in ["next monday", "tomorrow", "next week", "soon", "by end of week", "coming wednesday", "shortly", "as soon as possible", "next friday"]):
                needs_verification = True
                verification_reason = "Relative date mentioned without explicit calendar date. Student confirmation required."

            title = f"{found_subject or 'Academic'} Task"
            is_exam = any(k in p_clean.lower() for k in ["exam", "test", "internal", "midterm", "quiz", "assessment", "viva"])
            is_lab = any(k in p_clean.lower() for k in ["lab", "practical", "record", "observation"])
            is_project = any(k in p_clean.lower() for k in ["project", "synopsis", "presentation", "abstract"])
            is_event = any(k in p_clean.lower() for k in ["symposium", "workshop", "techfest", "hackathon", "seminar", "orientation", "lecture", "event"])

            if is_exam:
                category = "examination"
                title = f"{found_subject or 'Course'} Internal Examination"
            elif is_lab:
                category = "lab"
                title = f"{found_subject or 'Course'} Lab Submission"
            elif is_project:
                category = "project"
                title = f"{found_subject or 'Course'} Project Submission"
            elif is_event:
                category = "event"
                evt_match = re.search(r"['\"](.*?)['\"]|([A-Z][a-zA-Z\s]+(?:Symposium|Workshop|Hackathon|Fest|Lecture))", p_clean)
                title = evt_match.group(0) if evt_match else f"{found_subject or 'College'} Academic Event"
            else:
                category = "assignment"
                assign_match = re.search(r"(?:Assignment|Problem Set)\s*\d*", p_clean, re.IGNORECASE)
                assign_label = assign_match.group(0) if assign_match else "Assignment"
                title = f"{found_subject or 'Academic'} {assign_label}"

            instructions = []
            for instr_word in ["module", "prepare", "submit", "execute", "normalize", "attendance", "format", "upload"]:
                if instr_word in p_clean.lower():
                    instructions.append(p_clean[:120])
                    break

            deadline_val = extracted_date if category != "examination" and category != "event" else None
            event_val = extracted_date if category in ["examination", "event"] else None

            tasks.append(
                ExtractedTaskItem(
                    title=title,
                    subject=found_subject or "General",
                    category=category,
                    description=p_clean[:300],
                    deadline=deadline_val,
                    event_date=event_val,
                    instructions=instructions,
                    estimated_duration=3.0 if category in ["examination", "project"] else 2.0,
                    difficulty="Difficult" if category == "examination" else "Medium",
                    importance="Critical" if category == "examination" else "Normal",
                    needs_verification=needs_verification or (deadline_val is None and event_val is None),
                    verification_reason=verification_reason or ("Date not explicitly detected. Please verify or add date." if not (deadline_val or event_val) else None),
                    supporting_evidence=p_clean[:200]
                )
            )

        if not tasks:
            tasks.append(
                ExtractedTaskItem(
                    title="Academic Notice Task",
                    subject="General",
                    category="assignment",
                    description=text[:200],
                    deadline=None,
                    event_date=None,
                    instructions=[text[:100]],
                    estimated_duration=2.0,
                    needs_verification=True,
                    verification_reason="General announcement requiring student review to define tasks and deadlines.",
                    supporting_evidence=text[:150]
                )
            )

        return GeminiExtractionResult(
            tasks=tasks,
            raw_summary=f"Processed announcement ({len(tasks)} activities identified). Note: {reason}",
            ambiguity_detected=any(t.needs_verification for t in tasks),
            model_used=self.model_name,
            extraction_mode="deterministic_fallback"
        )

gemini_service = GeminiService()
