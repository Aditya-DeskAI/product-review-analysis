from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database.connection import Base

class RawScrapingData(Base):
    """Stores the raw reviews and comments extracted from the web."""
    __tablename__ = "raw_scraping_data"

    id = Column(Integer, primary_key=True, index=True)
    entity_name = Column(String, index=True) # e.g., "iphone 15 pro"
    source_url = Column(String)
    platform = Column(String) # e.g., "Reddit", "Amazon"
    raw_text = Column(String) # The actual user comment/review
    extracted_at = Column(DateTime(timezone=True), server_default=func.now())

    # Link back to the final review
    review_id = Column(Integer, ForeignKey("universal_reviews.id"))
    final_review = relationship("UniversalReview", back_populates="raw_data")


class UniversalReview(Base):
    """Stores the final, synthesized JSON analysis for the frontend."""
    __tablename__ = "universal_reviews"

    id = Column(Integer, primary_key=True, index=True)
    entity_name = Column(String, unique=True, index=True)
    
    # --- Top Level Searchable Metrics ---
    one_line_verdict = Column(String)
    overall_score = Column(Float)
    
    # --- The Core Nested Data (Stored as JSON for easy frontend parsing) ---
    quick_review_data = Column(JSON) 
    detailed_indicators = Column(JSON)
    decision_intelligence = Column(JSON)
    chart_metrics = Column(JSON)
    transparency_and_evidence = Column(JSON)
    
    # --- Metadata ---
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Link to all the raw reviews that generated this analysis
    raw_data = relationship("RawScrapingData", back_populates="final_review")