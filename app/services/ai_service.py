import os
import json
from typing import Dict, Any
from app.core.config import settings

class AIService:
    """
    AI Service
    Provides:
    1. Automated Ticket Classification (e.g. Royalty, Publishing, Distribution)
    2. Priority Assignment (Urgent, High, Medium, Low)
    3. Context-aware Reply Drafting for support staff
    
    Adheres strictly to the requirement that the AI API key is configured
    via environment variables and is never exposed to the frontend.
    """

    @classmethod
    async def analyze_and_draft(cls, subject: str, description: str, book_title: str = None) -> Dict[str, Any]:
        """
        Analyzes support query and generates classification, priority, and draft reply.
        Uses external LLM API if AI_API_KEY is configured, else uses intelligent fallback logic.
        """
        api_key = settings.AI_API_KEY

        if api_key:
            try:
                # If Google Gemini API is configured
                import urllib.request
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.AI_MODEL}:generateContent?key={api_key}"
                prompt = (
                    f"You are the BookLeaf AI Support Assistant. Analyze this author support query:\n"
                    f"Subject: {subject}\n"
                    f"Description: {description}\n"
                    f"Book: {book_title or 'General / Account Query'}\n\n"
                    f"Return a JSON object with:\n"
                    f"1. classification: One of ['Royalty & Payments', 'ISBN & Metadata Issues', 'Printing & Quality', 'Distribution & Availability', 'Book Status & Production Updates', 'General Inquiry']\n"
                    f"2. priority: One of ['Critical', 'High', 'Medium', 'Low'] (Critical if prolonged payout delays, severe printing defect, or missing ISBN)\n"
                    f"3. reply_draft: A professional, empathetic response draft for BookLeaf admin to review and send to the author."
                )
                payload = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode("utf-8")
                req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=10) as response:
                    result = json.loads(response.read().decode("utf-8"))
                    text = result["candidates"][0]["content"]["parts"][0]["text"]
                    # Extract JSON substring
                    start = text.find("{")
                    end = text.rfind("}") + 1
                    if start != -1 and end != 0:
                        return json.loads(text[start:end])
            except Exception:
                pass  # Fall back to heuristic engine

        # Heuristic / Rule-based Fallback Engine
        text_lower = f"{subject} {description}".lower()
        
        # Determine classification (as per BookLeaf specifications)
        if any(w in text_lower for w in ["royalty", "payout", "payment", "bank", "neft", "earned", "tds", "money", "threshold"]):
            category = "Royalty & Payments"
        elif any(w in text_lower for w in ["isbn", "metadata", "barcode", "imprint"]):
            category = "ISBN & Metadata Issues"
        elif any(w in text_lower for w in ["print", "quality", "binding", "paper", "blur", "misprint", "damage", "copies"]):
            category = "Printing & Quality"
        elif any(w in text_lower for w in ["amazon", "flipkart", "store", "distribution", "stock", "unavailable", "listing"]):
            category = "Distribution & Availability"
        elif any(w in text_lower for w in ["typesetting", "proofread", "cover", "editing", "production", "status", "manuscript", "live", "delay"]):
            category = "Book Status & Production Updates"
        else:
            category = "General Inquiry"

        # Determine priority (Critical / High / Medium / Low)
        if any(w in text_lower for w in ["critical", "urgent", "delayed 6 months", "missing payout", "unpaid", "legal", "duplicate isbn", "terrible quality"]):
            priority = "Critical"
        elif any(w in text_lower for w in ["error", "wrong", "cannot see", "failed", "delayed", "missing"]):
            priority = "High"
        elif any(w in text_lower for w in ["update", "question", "when", "change"]):
            priority = "Medium"
        else:
            priority = "Low"

        # Proposed Reply Draft
        book_mention = f" for '{book_title}'" if book_title else ""
        reply_draft = (
            f"Dear Author,\n\n"
            f"Thank you for reaching out regarding '{subject}'{book_mention}.\n\n"
            f"We have thoroughly reviewed your query and are investigating the details with our "
            f"{category} team. We will ensure this is resolved for you promptly.\n\n"
            f"Warm regards,\nBookLeaf Author Support Team"
        )

        return {
            "classification": category,
            "priority": priority,
            "reply_draft": reply_draft
        }
