from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
import tempfile
import logging

from app.pdf_processor import PDFProcessor
from app.ipo_analyzer import IPOAnalyzer
from app.chat_service import ChatService
from app.models.response_models import IPOAnalysisResponse
from app.models.chat_models import ChatRequest, ChatResponse

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

# Initialize processors and services
pdf_processor = PDFProcessor()
ipo_analyzer = IPOAnalyzer()
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY environment variable is required")
chat_service = ChatService(gemini_api_key=gemini_api_key)

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
        if not file.filename or not file.filename.lower().endswith('.pdf'):
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
            full_text, extracted_content = await pdf_processor.extract_content(temp_file_path)
            
            # Analyze for IPO readiness
            logger.info("Analyzing IPO readiness")
            analysis_result = await ipo_analyzer.analyse(
                content=full_text,
                extracted_content=extracted_content
            )
            
            # Store context for chat service
            chat_service.store_analysis_context(
                analysis_id=analysis_result.analysis_id,
                full_text=full_text,
                extracted_content=extracted_content,
                analysis_results=analysis_result.model_dump()
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

@app.post("/chat", response_model=ChatResponse)
async def chat_with_analysis(request: ChatRequest):
    """
    Chat with AI about the analysis results
    """
    try:
        response = await chat_service.chat(request)
        return response
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@app.get("/chat/conversations/{analysis_id}")
async def get_conversations_for_analysis(analysis_id: str):
    """
    Get all conversations for a specific analysis
    """
    try:
        conversations = chat_service.get_conversations_for_analysis(analysis_id)
        return {"conversations": [conv.model_dump() for conv in conversations]}
        
    except Exception as e:
        logger.error(f"Error getting conversations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get conversations: {str(e)}")

@app.get("/chat/history/{conversation_id}")
async def get_conversation_history(conversation_id: str):
    """
    Get conversation history by conversation ID
    """
    try:
        conversation = chat_service.get_conversation_history(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return conversation.model_dump()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get conversation history: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)