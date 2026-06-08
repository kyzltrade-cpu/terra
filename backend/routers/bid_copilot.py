import re

import pypdf
from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.services.bid_estimator import calculate_issa_labor_hours

router = APIRouter(prefix="/api/bid-copilot", tags=["bid-copilot"])


@router.post("/estimate")
async def estimate_bid(file: UploadFile = File(...)):
    try:
        pdf_reader = pypdf.PdfReader(file.file)
        text_content = ""
        for page in pdf_reader.pages:
            text_content += page.extract_text() or ""

        sqft_matches = re.findall(
            r"(\d{1,3}(?:,\d{3})*)\s*(?:sq\s*ft|sq\.?\s*ft|square\s*feet)",
            text_content,
            re.IGNORECASE,
        )
        total_sqft = sum(int(val.replace(",", "")) for val in sqft_matches) if sqft_matches else 5000

        estimated_hours = calculate_issa_labor_hours("carpet", total_sqft)
        return {
            "parsed_total_sqft": total_sqft,
            "estimated_weekly_labor_hours": estimated_hours,
            "recommended_pricing_bracket": {
                "low": round(estimated_hours * 25.0 * 4.3, 2),
                "high": round(estimated_hours * 35.0 * 4.3, 2),
            },
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse RFP document: {str(e)}")
