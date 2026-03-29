from pydantic import BaseModel
from typing import List, Dict, Any, Optional

# --- REQUEST FROM STREAMLIT ---
class ProductRequest(BaseModel):
    product_name: str

# --- AGENT 1: THE HUNTER (Raw Data) ---
class ExtractedReview(BaseModel):
    platform: str
    url: str
    raw_text: str

class RawExtractionResponse(BaseModel):
    """The JSON output from the browser-use scraping agent."""
    entity_name: str
    reviews: List[ExtractedReview]

# --- AGENT 2: THE SYNTHESIZER (Final Analysis) ---
class UniversalResponse(BaseModel):
    """The JSON output sent to the Streamlit frontend."""
    entity_name: str
    quick_review: Dict[str, Any]
    detailed_indicators: Dict[str, Any]
    decision_intelligence: List[Dict[str, str]]
    chart_metrics: Dict[str, Any]
    transparency_and_evidence: Dict[str, Any]