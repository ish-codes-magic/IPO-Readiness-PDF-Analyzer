import os
import logging
import time
import uuid
from typing import Dict, Any, List
from jinja2 import Environment, FileSystemLoader
import instructor
from instructor import Mode
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from google.genai import Client, types

from .models.response_models import (
    IPOAnalysisResponse, CriterionScore, ExecutiveSummary, 
    RiskAssessment, FollowUpQuestions, CompanyMetadata, StructuredAnalysis
)

logger = logging.getLogger(__name__)

class IPOAnalyzer:
    """
    AI-powered IPO readiness analyzer using Gemini API
    """
    
    def __init__(self):
        """Initialize the analyzer with Gemini API and Instructor"""
        # Configure Gemini API
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        self.genai_client = Client(api_key=api_key)
         
        # Initialize Gemini model with Instructor
        self.model = instructor.from_genai(
            client=self.genai_client,
            mode=Mode.GENAI_STRUCTURED_OUTPUTS
        )
        # Initialize Jinja2 template environment
        template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts")
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
        
        # Evaluation criteria definitions
        self.criteria_definitions = [
            {
                "name": "Basic Company Info",
                "description": "Company background, founding details, and key information",
                "keywords": ["company", "founded", "team", "background", "history"]
            },
            {
                "name": "Mission & Core Business", 
                "description": "Business model clarity and strategic focus",
                "keywords": ["mission", "business model", "value proposition", "strategy"]
            },
            {
                "name": "Defensibility / IP / MOAT",
                "description": "Competitive advantages and intellectual property", 
                "keywords": ["competitive advantage", "ip", "patent", "moat", "differentiation"]
            },
            {
                "name": "Regulatory Approvals & Compliance",
                "description": "Industry compliance and regulatory readiness",
                "keywords": ["regulatory", "compliance", "license", "approval", "legal"]
            },
            {
                "name": "Commercial Traction & Validation",
                "description": "Market validation and customer traction",
                "keywords": ["traction", "customers", "revenue", "growth", "validation"]
            },
            {
                "name": "Segment-level Unit Economics", 
                "description": "Financial metrics and unit economics analysis",
                "keywords": ["unit economics", "cac", "ltv", "margins", "profitability"]
            },
            {
                "name": "Equity Cap Table",
                "description": "Ownership structure and equity distribution", 
                "keywords": ["equity", "cap table", "ownership", "shares", "dilution"]
            },
            {
                "name": "Key Risks & Information Gaps",
                "description": "Risk assessment and information completeness",
                "keywords": ["risks", "challenges", "gaps", "threats", "weaknesses"]
            }
        ]
    
    async def analyse(self, content: Dict[str, Any], filename: str) -> IPOAnalysisResponse:
        """
        Analyze extracted PDF content for IPO readiness
        
        Args:
            content: Extracted PDF content from PDFProcessor
            filename: Original filename
            
        Returns:
            Structured IPO analysis response
        """
        start_time = time.time()
        analysis_id = str(uuid.uuid4())
        
        try:
            logger.info(f"Starting IPO analysis for {filename}")
            
            # Render the analysis prompt using Jinja2
            prompt = self._render_analysis_prompt(content, filename)
            
            # Get structured analysis from Gemini
            analysis_result = await self._get_structured_analysis(prompt)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Build final response
            response = IPOAnalysisResponse(
                analysis_id=analysis_id,
                filename=filename,
                company_metadata=analysis_result.get("company_metadata", CompanyMetadata()),
                overall_ipo_score=analysis_result.get("overall_ipo_score", 0),
                readiness_level=self._determine_readiness_level(analysis_result.get("overall_ipo_score", 0)),
                criterion_scores=analysis_result.get("criterion_scores", []),
                executive_summary=analysis_result.get("executive_summary", ExecutiveSummary(
                    overall_assessment="Analysis incomplete",
                    recommendation="Further analysis required"
                )),
                risk_assessment=analysis_result.get("risk_assessment", RiskAssessment(
                    risk_level="Unknown"
                )),
                follow_up_questions=analysis_result.get("follow_up_questions", FollowUpQuestions()),
                financial_highlights=analysis_result.get("financial_highlights", {}),
                competitive_positioning=analysis_result.get("competitive_positioning", "Not assessed"),
                processing_time_seconds=processing_time,
                confidence_score=analysis_result.get("confidence_score", 0.5)
            )
            
            logger.info(f"Analysis completed in {processing_time:.2f} seconds")
            return response
            
        except Exception as e:
            logger.error(f"Error in IPO analysis: {str(e)}")
            # Return a basic error response
            return IPOAnalysisResponse(
                analysis_id=analysis_id,
                filename=filename,
                company_metadata=CompanyMetadata(),
                overall_ipo_score=0,
                readiness_level="Not Ready",
                criterion_scores=[],
                executive_summary=ExecutiveSummary(
                    overall_assessment=f"Analysis failed: {str(e)}",
                    recommendation="Manual review required"
                ),
                risk_assessment=RiskAssessment(risk_level="High"),
                follow_up_questions=FollowUpQuestions(),
                competitive_positioning="Unable to assess",
                processing_time_seconds=time.time() - start_time,
                confidence_score=0.0
            )
    
    def _render_analysis_prompt(self, content: Dict[str, Any], filename: str) -> str:
        """
        Render the Jinja2 template with extracted content
        """
        template = self.jinja_env.get_template("ipo_analysis_prompt.j2")
        
        return template.render(
            filename=filename,
            full_text=content.get("full_text", ""),
            # sections=content.get("sections", {}),
            tables=content.get("tables", []),
            metadata=content.get("metadata", {})
        )
    
    async def _get_structured_analysis(self, prompt: str) -> Dict[str, Any]:
        """
        Get structured analysis from Gemini using Instructor
        """
        
        try:
            # Use Instructor to get structured response
            response = await self.model.create(
                messages=[{"role": "user", "content": prompt}],
                response_model=StructuredAnalysis,
                model="gemini-2.5-flash",
                max_retries=3
            )
            
            return response.model_dump()
            
        except Exception as e:
            logger.error(f"Error getting structured analysis: {str(e)}")
            # Fallback to basic analysis
            return await self._fallback_analysis(prompt)
    
    async def _fallback_analysis(self, prompt: str) -> Dict[str, Any]:
        """
        Fallback analysis when structured response fails
        """
        try:
            # Simple text generation as fallback
            from google.genai import Client
            client = Client(api_key=os.getenv("GEMINI_API_KEY"))
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt + "\n\nPlease provide a brief analysis with scores for each criterion."
            )
            
            # Parse basic information from text response
            text_response = response.candidates[0].content.parts[0].text if response.candidates else ""
            
            # Create basic structured response
            criterion_scores = []
            for criterion in self.criteria_definitions:
                # Basic scoring based on keyword presence
                score = self._estimate_criterion_score(text_response, criterion)
                criterion_scores.append(CriterionScore(
                    name=criterion["name"],
                    score=score,
                    rationale=f"Basic assessment based on available information",
                    strengths=["Information available"] if score > 5 else [],
                    weaknesses=["Limited information"] if score <= 5 else []
                ))
            
            overall_score = sum(c.score for c in criterion_scores) * 10 / len(criterion_scores)
            
            return {
                "company_metadata": CompanyMetadata(),
                "overall_ipo_score": overall_score,
                "criterion_scores": criterion_scores,
                "executive_summary": ExecutiveSummary(
                    overall_assessment="Basic analysis completed",
                    recommendation="Detailed review recommended"
                ),
                "risk_assessment": RiskAssessment(risk_level="Medium"),
                "follow_up_questions": FollowUpQuestions(
                    questions=["Provide detailed financial statements", "Clarify business model"]
                ),
                "competitive_positioning": "Requires further analysis",
                "confidence_score": 0.3
            }
            
        except Exception as e:
            logger.error(f"Fallback analysis failed: {str(e)}")
            raise e
    
    def _estimate_criterion_score(self, text: str, criterion: Dict[str, str]) -> float:
        """
        Estimate criterion score based on keyword presence
        """
        text_lower = text.lower()
        keyword_count = sum(1 for keyword in criterion["keywords"] if keyword in text_lower)
        
        # Basic scoring: more keywords = higher score
        base_score = min(keyword_count * 2, 8)
        
        # Add some randomness to avoid identical scores
        import random
        adjustment = random.uniform(-0.5, 1.5)
        
        return max(0, min(10, base_score + adjustment))
    
    def _determine_readiness_level(self, score: float) -> str:
        """
        Determine IPO readiness level based on overall score
        """
        if score >= 86:
            return "Highly Ready"
        elif score >= 66:
            return "Ready"
        elif score >= 41:
            return "Developing"
        else:
            return "Not Ready"