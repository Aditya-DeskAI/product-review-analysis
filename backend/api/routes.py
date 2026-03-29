from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import traceback

from backend.database.connection import get_db
from backend.database.models import UniversalReview, RawScrapingData
from backend.utils.data_parser import ProductRequest, UniversalResponse
from backend.agent.tasks import extract_raw_data, synthesize_final_analysis

router = APIRouter()

@router.post("/analyze-product", response_model=UniversalResponse)
async def analyze_product(request: ProductRequest, db: Session = Depends(get_db)):
    entity_name_lower = request.product_name.lower().strip()

    # ==========================================
    # STAGE 1: CACHE CHECK
    # ==========================================
    cached_entity = db.query(UniversalReview).filter(
        UniversalReview.entity_name.ilike(entity_name_lower)
    ).first()

    if cached_entity:
        print(f"[API] Returning fully cached analysis for: {request.product_name}")
        return UniversalResponse(
            entity_name=cached_entity.entity_name,
            quick_review=cached_entity.quick_review_data,
            detailed_indicators=cached_entity.detailed_indicators,
            decision_intelligence=cached_entity.decision_intelligence,
            chart_metrics=cached_entity.chart_metrics,
            transparency_and_evidence=cached_entity.transparency_and_evidence
        )

    print(f"[API] No cache found. Beginning deep research for: {request.product_name}...")

    # ==========================================
    # STAGE 2: THE HUNTER (Extract Raw Data)
    # ==========================================
    try:
        raw_extraction_dict = await extract_raw_data(entity_name_lower)
        reviews_list = raw_extraction_dict.get("reviews", [])
    except Exception as e:
        print("[API ERROR] The Hunter failed to extract data.")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Hunter Failed: {str(e)}")

    if not reviews_list:
        raise HTTPException(status_code=500, detail="The Hunter agent returned 0 raw reviews. Cannot proceed.")

    # ==========================================
    # STAGE 3: THE SYNTHESIZER (Generate Charts)
    # ==========================================
    try:
        final_analysis_dict = await synthesize_final_analysis(entity_name_lower, raw_extraction_dict)
    except Exception as e:
        print("[API ERROR] The Synthesizer failed to analyze data.")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Synthesizer Failed: {str(e)}")

    # ==========================================
    # STAGE 4: STORE EVERYTHING IN THE DATABASE
    # ==========================================
    try:
        overall_score = final_analysis_dict.get("detailed_indicators", {}).get("1_overall_verdict", {}).get("score_out_of_10", 0.0)
        
        # 4a. Create the final analysis row
        new_review = UniversalReview(
            entity_name=entity_name_lower,
            one_line_verdict=final_analysis_dict.get("quick_review", {}).get("one_line_verdict", "No verdict provided."),
            overall_score=overall_score,
            quick_review_data=final_analysis_dict.get("quick_review", {}),
            detailed_indicators=final_analysis_dict.get("detailed_indicators", {}),
            decision_intelligence=final_analysis_dict.get("decision_intelligence", []),
            chart_metrics=final_analysis_dict.get("chart_metrics", {}),
            transparency_and_evidence=final_analysis_dict.get("transparency_and_evidence", {})
        )
        db.add(new_review)
        db.flush() # Flushes to generate the `new_review.id` needed for the Raw Data foreign key

        # 4b. Create a database row for EVERY single raw review extracted
        for review in reviews_list:
            raw_db_entry = RawScrapingData(
                entity_name=entity_name_lower,
                source_url=review.get("url", ""),
                platform=review.get("platform", "Unknown"),
                raw_text=review.get("raw_text", ""),
                review_id=new_review.id # Link it to the final analysis
            )
            db.add(raw_db_entry)

        # 4c. Commit the massive transaction to SQLite
        db.commit()
        db.refresh(new_review)
        print(f"[API] Successfully saved analysis and {len(reviews_list)} raw quotes to the database.")
        
    except Exception as db_err:
        print(f"[API DB ERROR] Failed to save to database: {db_err}")
        db.rollback()
        # Even if DB fails, we still return the data to the user so the frontend works
        pass

    return final_analysis_dict