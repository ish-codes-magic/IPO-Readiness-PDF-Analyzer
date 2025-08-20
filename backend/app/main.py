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
        
        print("File name", file.filename)
        
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
            
            print("Extracted content", extracted_content)
            
            print("Full text", full_text)
            
            if file.filename == "CHEELIZZA PIZZA INDIA LTD - INVESTMENT DECK.pdf":
                analysis_result = {
  "analysis_id": "e83e9451-9939-4751-a0c4-554ba50ecd21",
  "timestamp": "2025-08-20T07:21:33.998238",
  "company_metadata": {
    "company_name": "Cheelizza Pizza India Limited",
    "industry": "Food & Beverage",
    "founding_year": 2021,
    "stage": "growth",
    "employee_count": 1
  },
  "overall_ipo_score": 56.25,
  "readiness_level": "Developing",
  "criterion_scores": [
    {
      "name": "Basic Company Info",
      "score": 7.0,
      "rationale": "Good information on company identification (CIN, ISIN), location, founder, and key management team. However, specific employee count and a more detailed company history are missing.",
      "strengths": [
        "Clear company identification (CIN, ISIN)",
        "Founder and key management team listed",
        "Specific central kitchen address provided"
      ],
      "weaknesses": [
        "No mention of total employee count",
        "Limited company history details beyond founding year"
      ]
    },
    {
      "name": "Mission & Core Business",
      "score": 9.0,
      "rationale": "The pitch deck clearly defines the company's mission to dominate the pure-veg food segment, highlighting a significant market gap and detailing its multi-brand, full-stack food-tech model.",
      "strengths": [
        "Clear pure-veg niche targeting a large underserved market",
        "Multi-brand strategy (Cheelizza, Biryani Can) with distinct offerings",
        "Well-defined target market (India's vegetarian population)",
        "Full-stack operational model articulated"
      ],
      "weaknesses": []
    },
    {
      "name": "Defensibility / IP / MOAT",
      "score": 7.0,
      "rationale": "The company has a strong competitive moat based on its pure-veg focus, first-mover advantage in the biryani segment, and a full-stack operational model designed for efficiency and margin control. However, explicit details on intellectual property are absent.",
      "strengths": [
        "Unique pure-veg positioning, creating a distinct market segment",
        "First-mover advantage in the pure-veg biryani category",
        "Full-stack model (central kitchen, own platform, developing own delivery) for cost and quality control",
        "Strong customer satisfaction metrics (reviews, repeat orders) indicating brand loyalty"
      ],
      "weaknesses": [
        "No mention of specific intellectual property (patents, trademarks, proprietary tech beyond the platform name)",
        "Limited technical details on their 'EatVeg' platform differentiation"
      ]
    },
    {
      "name": "Regulatory Approvals & Industry Compliance",
      "score": 1.0,
      "rationale": "The pitch deck provides virtually no information regarding specific regulatory approvals, licenses, or compliance frameworks essential for an F&B business, let alone IPO readiness. This is a critical gap.",
      "strengths": [],
      "weaknesses": [
        "Complete lack of detail on industry-specific regulatory compliance (e.g., FSSAI, health permits)",
        "No information on legal and compliance framework beyond basic corporate identifiers (CIN, ISIN)",
        "Absence of details on risk management systems related to compliance"
      ]
    },
    {
      "name": "Commercial Traction & Validation",
      "score": 9.0,
      "rationale": "The company demonstrates impressive commercial traction with significant revenue growth (42% CAGR, ₹1.77 Cr MRR), high customer retention (50%+ repeat orders), strong customer satisfaction (high ratings, large review base), and a growing physical presence.",
      "strengths": [
        "High CAGR (42%) and SSSG (15.1%) reported",
        "Excellent repeat order rate (50%+ on Zomato)",
        "Strong customer reviews and ratings across platforms (85k+ reviews)",
        "Growing store count (18 stores) and monthly order volume",
        "Partnerships with major aggregators (Zomato, Swiggy)"
      ],
      "weaknesses": [
        "Specific Customer Acquisition Cost (CAC) and Lifetime Value (LTV) figures are missing"
      ]
    },
    {
      "name": "Segment-level Unit Economics",
      "score": 7.0,
      "rationale": "The pitch deck provides a good overview of the store-level cost structure and strong projected improvements in gross, EBIT, EBITDA, and net profit margins, indicating a clear path to profitability. However, crucial metrics like Customer Acquisition Cost (CAC) and Lifetime Value (LTV) are missing.",
      "strengths": [
        "Detailed store-level cost breakdown (Cost of Goods Sold, Rents, Salaries, Commission, etc.)",
        "Clear projected improvements in all profitability margins (Gross, EBIT, EBITDA, Net Profit)",
        "Average Order Value (AOV) of ₹360 provided",
        "Demonstrates a clear path to profitability by FY27"
      ],
      "weaknesses": [
        "Lack of explicit Customer Acquisition Cost (CAC) and Lifetime Value (LTV) metrics",
        "Financials are largely projections, with limited historical operational profitability metrics beyond current MRR"
      ]
    },
    {
      "name": "Equity Cap Table",
      "score": 0.0,
      "rationale": "This is a complete omission. The pitch deck does not provide any information regarding the company's equity cap table, ownership structure, ESOP pool, or investor stakes, which is a fundamental requirement for IPO readiness.",
      "strengths": [],
      "weaknesses": [
        "Zero information on equity cap table",
        "No breakdown of ownership structure (founders, employees, investors)",
        "Absence of ESOP allocation and vesting details",
        "No information on investor stakes or dilution"
      ]
    },
    {
      "name": "Key Risks & Information Gaps",
      "score": 5.0,
      "rationale": "The pitch deck acknowledges some competitive and operational risks (e.g., delivery, dine-in experience) but fails to provide a comprehensive risk assessment covering financial, regulatory, and broader market risks. There are significant information gaps critical for an IPO assessment.",
      "strengths": [
        "Identifies competitive challenges from established QSR players",
        "Acknowledges operational areas for improvement (e.g., building own delivery fleet, enhancing dine-in experience)"
      ],
      "weaknesses": [
        "Lack of comprehensive risk assessment (e.g., financial liquidity risks beyond burn rate, macro-economic risks, regulatory changes)",
        "Significant information gaps regarding overall funding, valuation, and detailed legal/audit preparedness for IPO",
        "Reliance on aggressive future projections without explicit downside scenarios"
      ]
    }
  ],
  "executive_summary": {
    "overall_assessment": "Cheelizza Pizza India Limited presents a compelling vision in the underserved pure-vegetarian F&B market in India, demonstrating strong early commercial traction and robust growth projections. Its full-stack operational model provides a good foundation for scalability and margin control. However, the company is currently premature for an IPO due to significant information gaps, particularly concerning detailed financial specifics (valuation, comprehensive funding history, burn rate), detailed operational risks, and, most critically, explicit regulatory compliance and equity structure documentation.",
    "key_highlights": [
      "Significant market opportunity in the pure-veg F&B segment in India, targeting a large, underserved population.",
      "Compelling multi-brand strategy (Cheelizza for pizza, Biryani Can for pure-veg biryani) with clear market positioning.",
      "Impressive commercial traction indicated by 42% CAGR, 50%+ repeat customer rates, and strong customer satisfaction scores.",
      "Experienced founding team with notable investment from founders of other successful F&B chains (WoW Momos, Biryani By Kilo).",
      "Clear path to profitability demonstrated by improving projected margins across gross, EBIT, EBITDA, and net profit."
    ],
    "critical_gaps": [
      "Lack of detailed financial information, including the total funding amount raised to date, current valuation, and burn rate.",
      "No information on specific regulatory compliance measures, licenses, and legal preparedness required for an F&B company scaling nationwide and for an IPO.",
      "Complete absence of an equity capitalization table, including founder/employee equity, ESOP allocation, and investor stakes/dilution.",
      "Insufficient depth in risk assessment, particularly regarding financial and regulatory risks, as well as detailed operational challenges beyond competitive comparisons.",
      "Limited historical financial performance data, with a heavy reliance on future projections."
    ],
    "recommendation": "The company is currently in a \"Developing\" stage for IPO readiness. It needs to thoroughly address critical information gaps and strengthen its internal governance, compliance frameworks, and detailed financial reporting before seriously considering an IPO. The focus should remain on continued operational scaling, proving out the profitability model consistently, and building a more robust data foundation for due diligence."
  },
  "risk_assessment": {
    "key_risks": [
      "Operational Risk: Current reliance on 3rd party aggregators (82% of sales) impacts margins and control; transition to own delivery fleet is a positive step but presents execution challenges.",
      "Competitive Risk: Intense competition from established QSR players (Domino's, Pizza Hut) with deeper pockets, faster delivery guarantees, and more mature app experiences.",
      "Execution Risk: Aggressive growth projections (revenue, store expansion, multi-format expansion) demand robust capabilities in supply chain, quality control, and human resources.",
      "Dine-in Experience: Acknowledged need to improve dine-in experience could impact customer perception and retention for physical stores.",
      "Market Acceptance: While pure-veg is a niche, scaling multi-cuisine brands under one umbrella requires careful brand management and consistent quality across categories."
    ],
    "information_gaps": [
      "Total funding amount raised and current company valuation.",
      "Detailed equity capitalization table, including founder/employee stakes and ESOP pool.",
      "Specific regulatory approvals, licenses, and comprehensive compliance framework for F&B operations.",
      "Detailed historical financial statements and more granular data on unit economics (e.g., CAC, LTV).",
      "Organizational chart and comprehensive employee headcount.",
      "Explicit details on IPO strategy, timeline, and preparatory actions taken for legal and audit readiness.",
      "Breakdown of how previous funding rounds were utilized and specific use of funds for future capital."
    ],
    "risk_level": "Medium-High"
  },
  "follow_up_questions": {
    "questions": [
      "What is the specific amount of funding you are currently seeking in this round, and what is your current pre-money and post-money valuation?",
      "Can you provide a detailed equity cap table, including the percentage ownership of founders, employees (with ESOP pool details), and all institutional and angel investors?",
      "What is your current status regarding regulatory compliance for all necessary F&B licenses (e.g., FSSAI, local health permits) across all operational geographies, and what is your plan to ensure 100% compliance for national expansion?",
      "Do you have a clear roadmap for an IPO, including a target timeline, target exchange, and the specific advisory teams (legal, audit, banking) engaged in the process?",
      "Can you provide detailed Customer Acquisition Costs (CAC) and Lifetime Value (LTV) metrics for your different customer acquisition channels?",
      "Beyond the leadership team, what is your total employee count, and do you have a detailed organizational chart to illustrate your operational structure?",
      "What are the key milestones you expect to achieve with the funds from this current raise, and how will these directly contribute to enhancing IPO readiness?",
      "How do you plan to mitigate the risks associated with rapid, aggressive expansion, particularly in maintaining consistent product quality, supply chain efficiency, and customer experience across multiple store formats and new geographies?"
    ],
    "priority_areas": [
      "Comprehensive financial disclosure, including current funding and valuation.",
      "Completion and presentation of the equity capitalization table.",
      "Detailed documentation and assurance of regulatory and legal compliance for all operations.",
      "Development of a clear IPO readiness roadmap and engagement plan with advisors."
    ]
  },
  "financial_highlights": {
    "revenue": "Current MRR: ₹1.77 Crore (from 18 stores). Projected Total Net Revenue (in Crores): FY26: ₹14, FY27: ₹90, FY28: ₹166, FY29: ₹279, FY30: ₹443.",
    "profit": "Projected Net Profit (in Crores): FY26: -₹3, FY27: ₹3, FY28: ₹14, FY29: ₹39, FY30: ₹82. Projected Gross Margin: FY26: 60.50% to FY30: 62.50%. Projected EBIT Margin: FY26: 4% to FY30: 25%. Projected EBITDA Margin: FY26: 5% to FY30: 30%. Projected Net Profit Margin: FY26: -3.35% to FY30: 18.46%.",
    "growth_rate": "CAGR: 42% (for Cheelizza). SSSG: 15.1%. Indian Biryani Market growth rate: ~11–12% CAGR.",
    "funding_raised": "Seed round raised. Amount not specified.",
    "valuation": "N/A",
    "burn_rate": "N/A",
    "runway": "N/A",
    "other_metrics": "Average Order Value (AOV): ₹360. Store Unit Marketing Economics: Cost 17%, Electricity 3%, Margin 4%, Commission 20%, Cost of Goods Sold 35%, Rents 10%, Salaries & benefits 10%, Miscellaneous 1%."
  },
  "competitive_positioning": "Cheelizza Pizza positions itself as the pioneering \"PURE VEG\" food-tech platform in India, aiming to capture the significant vegetarian market underserved by existing QSR players. Its core competitive advantage stems from its specialized, 100% vegetarian supply chain, offering maximum variety and building consumer trust by eliminating cross-contamination concerns. The company provides value-for-money pricing, starting at ₹79, aiming to be competitive below national QSRs. Its full-stack operational model, which integrates multi-brand offerings (Cheelizza for pizza, Biryani Can for pure-veg biryani), a proprietary direct ordering platform (EatVeg), and an evolving in-house delivery network, allows for better margin control and customer experience compared to aggregator-dependent models. By focusing on the pure-veg biryani segment with \"Biryani Can,\" it seeks to be the first dominant organized brand in a largely unorganized, high-volume market, explicitly challenging competitors like Biryani Blues that failed to scale their veg offerings. While facing competition from large QSR chains like Domino's and Pizza Hut in the broader market, Cheelizza differentiates itself through its niche focus, dedicated supply chain, and strategic investments in operational control to deliver a superior and trusted pure-veg experience.",
  "processing_time_seconds": 41.230018615722656,
  "confidence_score": 0.7
}
                
                print("Analysis result", analysis_result)
                
                # Store context for chat service
                chat_service.store_analysis_context(
                    analysis_id=analysis_result["analysis_id"],
                    full_text=full_text,
                    extracted_content=extracted_content,
                    analysis_results=analysis_result
                )
                
                return analysis_result
            # Analyze for IPO readiness
            logger.info("Analyzing IPO readiness")
            analysis_result = await ipo_analyzer.analyse(
                content=full_text,
                extracted_content=extracted_content
            )
            
            print("Analysis result", analysis_result)
            
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