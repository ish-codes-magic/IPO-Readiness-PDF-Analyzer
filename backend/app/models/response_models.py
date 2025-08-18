from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class CriterionScore(BaseModel):
    """Individual criterion evaluation"""
    name: str = Field(..., description="Name of the evaluation criterion")
    score: float = Field(..., ge=0, le=10, description="Score out of 10")
    rationale: str = Field(..., description="Brief explanation of the score")
    strengths: List[str] = Field(default_factory=list, description="Key strengths identified")
    weaknesses: List[str] = Field(default_factory=list, description="Areas of concern or weakness")

class RiskAssessment(BaseModel):
    """Risk and gap analysis"""
    key_risks: List[str] = Field(default_factory=list, description="Major risks identified")
    information_gaps: List[str] = Field(default_factory=list, description="Missing information for IPO readiness")
    risk_level: str = Field(..., description="Overall risk level: Low, Medium, High")

class FollowUpQuestions(BaseModel):
    """Questions for next meeting"""
    questions: List[str] = Field(default_factory=list, description="Specific questions to ask in next meeting")
    priority_areas: List[str] = Field(default_factory=list, description="Areas requiring immediate attention")

class ExecutiveSummary(BaseModel):
    """Executive summary of the analysis"""
    overall_assessment: str = Field(..., description="High-level assessment of IPO readiness")
    key_highlights: List[str] = Field(default_factory=list, description="Major strengths to highlight to investors")
    critical_gaps: List[str] = Field(default_factory=list, description="Critical areas that need addressing")
    recommendation: str = Field(..., description="Overall recommendation regarding IPO timing")

class CompanyMetadata(BaseModel):
    """Basic company information extracted"""
    company_name: Optional[str] = Field(None, description="Company name if identifiable")
    industry: Optional[str] = Field(None, description="Industry sector")
    founding_year: Optional[int] = Field(None, description="Year founded")
    stage: Optional[str] = Field(None, description="Business stage (startup, growth, mature)")
    employee_count: Optional[int] = Field(None, description="Number of employees")
    
class StructuredAnalysis(BaseModel):
    company_metadata: CompanyMetadata
    overall_ipo_score: float = Field(..., ge=0, le=100)
    criterion_scores: List[CriterionScore]
    executive_summary: ExecutiveSummary
    risk_assessment: RiskAssessment
    follow_up_questions: FollowUpQuestions
    financial_highlights: Dict[str, Any] = Field(default_factory=dict)
    competitive_positioning: str
    confidence_score: float = Field(..., ge=0, le=1)

class IPOAnalysisResponse(BaseModel):
    """Complete IPO readiness analysis response"""
    analysis_id: str = Field(..., description="Unique identifier for this analysis")
    timestamp: datetime = Field(default_factory=datetime.now, description="Analysis timestamp")
    
    # Company metadata
    company_metadata: CompanyMetadata = Field(..., description="Basic company information")
    
    # Overall scoring
    overall_ipo_score: float = Field(..., ge=0, le=100, description="Overall IPO readiness score (0-100)")
    readiness_level: str = Field(..., description="IPO readiness level: Not Ready, Developing, Ready, Highly Ready")
    
    # Detailed criterion scores
    criterion_scores: List[CriterionScore] = Field(..., description="Detailed scores for each evaluation criterion")
    
    # Analysis components
    executive_summary: ExecutiveSummary = Field(..., description="Executive summary of findings")
    risk_assessment: RiskAssessment = Field(..., description="Risk and gap analysis")
    follow_up_questions: FollowUpQuestions = Field(..., description="Questions for next meeting")
    
    # Additional insights
    financial_highlights: Dict[str, Any] = Field(default_factory=dict, description="Key financial metrics identified")
    competitive_positioning: str = Field(..., description="Assessment of competitive position")
    
    # Processing metadata
    processing_time_seconds: float = Field(..., description="Time taken to process the analysis")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence in the analysis (0-1)")

class AnalysisError(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    error_type: str = Field(..., description="Type of error")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")