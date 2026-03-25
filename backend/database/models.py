from sqlalchemy import Column, Integer, String, JSON
from backend.database.connection import Base

class ProductReview(Base):
    __tablename__ = "product_reviews"

    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, unique=True, index=True)
    overall_summary = Column(String)
    average_sentiment_score = Column(Integer)
    pros = Column(JSON) # Stores list of pros
    cons = Column(JSON) # Stores list of cons
    platforms_scraped = Column(JSON)