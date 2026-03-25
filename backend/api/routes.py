from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.connection import get_db
from backend.database.models import ProductReview
from backend.utils.data_parser import ProductRequest, ProductResponse
from backend.agent.tasks import run_browser_agent

router = APIRouter()

@router.post("/analyze-product", response_model=ProductResponse)
async def analyze_product(request: ProductRequest, db: Session = Depends(get_db)):
    product_name_lower = request.product_name.lower().strip()

    # 1. Check if we already have this product in our database cache
    cached_product = db.query(ProductReview).filter(
        ProductReview.product_name.ilike(product_name_lower)
    ).first()

    if cached_product:
        print(f"Returning cached data for {request.product_name}")
        return ProductResponse(
            product_name=cached_product.product_name,
            overall_summary=cached_product.overall_summary,
            average_sentiment_score=cached_product.average_sentiment_score,
            pros=cached_product.pros,
            cons=cached_product.cons,
            platforms_scraped=cached_product.platforms_scraped
        )

    # 2. If not in DB, run the browser-use agent
    print(f"No cache found. Starting AI Agent for {request.product_name}...")
    try:
        agent_data = await run_browser_agent(product_name_lower)
    except Exception as e:
        import traceback
        traceback.print_exc() # <--- THIS WILL PRINT THE REAL ERROR IN THE TERMINAL
        raise HTTPException(status_code=500, detail=str(e))

    # 3. Save the new results to the database for future use
    new_review = ProductReview(
        product_name=product_name_lower,
        overall_summary=agent_data.get("overall_summary", "No summary provided."),
        average_sentiment_score=agent_data.get("average_sentiment_score", 50),
        pros=agent_data.get("pros", []),
        cons=agent_data.get("cons", []),
        platforms_scraped=agent_data.get("platforms_scraped", [])
    )
    db.add(new_review)
    db.commit()
    db.refresh(new_review)

    return agent_data