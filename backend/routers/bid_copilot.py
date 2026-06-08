import pypdf
from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.services.bid_estimator import estimate_bid_via_nim

router = APIRouter(prefix="/api/bid-copilot", tags=["bid-copilot"])


@router.post("/estimate")
async def estimate_bid(file: UploadFile = File(...)):
    try:
        pdf_reader = pypdf.PdfReader(file.file)
        text_content = ""
        for page in pdf_reader.pages:
            text_content += page.extract_text() or ""

        estimation = estimate_bid_via_nim(text_content)
        return estimation
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse RFP document: {str(e)}")
