from pydantic import BaseModel
from typing import List

# Request from Streamlit
class ProductRequest(BaseModel):
    product_name: str

# Response sent back to Streamlit
class ProductResponse(BaseModel):
    product_name: str
    overall_summary: str
    average_sentiment_score: int
    pros: List[str]
    cons: List[str]
    platforms_scraped: List[str]