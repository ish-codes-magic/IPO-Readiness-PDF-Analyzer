from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv
import tempfile
import logging
from typing import Dict, Any

from pdf_processor import PDFProcessor
from ipo_analyzer import IPOAnalyzer
from models.response_models import IPOAnalysisResponse

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="IPO Readiness PDF Analyzer",
    description="AI-powered platform for analyzing SME pitch decks and scoring IPO readiness",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize processors
pdf_processor = PDFProcessor()
ipo_analyzer = IPOAnalyzer()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "IPO Readiness PDF Analyzer API", "status": "active"}

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "gemini_api_configured": bool(os.getenv("GEMINI_API_KEY")),
        "version": "1.0.0"
    }

@app.post("/analyze-pdf", response_model=IPOAnalysisResponse)
async def analyze_pdf(file: UploadFile = File(...)):
    """
    Analyze uploaded PDF for IPO readiness
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Read file content
        content = await file.read()
        
        # Validate file size (20MB limit)
        max_size = 20 * 1024 * 1024  # 20MB in bytes
        if len(content) > max_size:
            raise HTTPException(status_code=400, detail="File size must be less than 20MB")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Extract content from PDF
            logger.info(f"Processing PDF: {file.filename}")
            full_text, extracted_content = pdf_processor.extract_content(temp_file_path)
            
            # Analyze for IPO readiness
            logger.info("Analyzing IPO readiness")
            analysis_result = await ipo_analyzer.analyse(
                content=full_text,
                extracted_content=extracted_content
            )
            
            return analysis_result
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as e:
        logger.error(f"Error analyzing PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/criteria")
async def get_evaluation_criteria():
    """
    Get the evaluation criteria used for IPO readiness scoring
    """
    return {
        "criteria": [
            {
                "name": "Basic Company Info",
                "description": "Company background, founding details, and key information",
                "weight": 12.5
            },
            {
                "name": "Mission & Core Business",
                "description": "Business model clarity and strategic focus",
                "weight": 12.5
            },
            {
                "name": "Defensibility / IP / MOAT",
                "description": "Competitive advantages and intellectual property",
                "weight": 12.5
            },
            {
                "name": "Regulatory Approvals & Compliance",
                "description": "Industry compliance and regulatory readiness",
                "weight": 12.5
            },
            {
                "name": "Commercial Traction & Validation",
                "description": "Market validation and customer traction",
                "weight": 12.5
            },
            {
                "name": "Segment-level Unit Economics",
                "description": "Financial metrics and unit economics analysis",
                "weight": 12.5
            },
            {
                "name": "Equity Cap Table",
                "description": "Ownership structure and equity distribution",
                "weight": 12.5
            },
            {
                "name": "Key Risks & Information Gaps",
                "description": "Risk assessment and information completeness",
                "weight": 12.5
            }
        ],
        "scoring_range": "0-100",
        "description": "Each criterion is weighted equally (12.5%) for the overall IPO readiness score"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)