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
                    f"1. classification: One of ['Royalty & Payouts', 'Publishing & Editing', 'Distribution & Inventory', 'Account & Profile', 'General Inquiry']\n"
                    f"2. priority: One of ['Urgent', 'High', 'Medium', 'Low'] (Urgent if payout delays or legal issues)\n"
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
        
        # Determine classification
        if any(w in text_lower for w in ["royalty", "payout", "payment", "bank", "neft", "earned", "tds"]):
            category = "Royalty & Payouts"
        elif any(w in text_lower for w in ["publish", "cover", "isbn", "manuscript", "format", "edit"]):
            category = "Publishing & Editing"
        elif any(w in text_lower for w in ["amazon", "flipkart", "stock", "copies", "delivery", "order"]):
            category = "Distribution & Inventory"
        elif any(w in text_lower for w in ["password", "login", "email", "profile", "phone"]):
            category = "Account & Profile"
        else:
            category = "General Inquiry"

        # Determine priority
        if any(w in text_lower for w in ["urgent", "delayed", "missing payout", "unpaid", "legal", "discrepancy"]):
            priority = "Urgent"
        elif any(w in text_lower for w in ["error", "wrong", "cannot see", "failed"]):
            priority = "High"
        else:
            priority = "Medium"

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
