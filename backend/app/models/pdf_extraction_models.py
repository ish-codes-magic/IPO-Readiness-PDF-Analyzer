from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class ExtractedTable(BaseModel):
    """Model for extracted table data"""
    title: str = Field(..., description="Title or caption of the table")
    headers: List[str] = Field(default_factory=list, description="Column headers")
    rows: List[List[str]] = Field(default_factory=list, description="Table rows data")
    page_number: int = Field(..., description="Page number where table was found")
    context: str = Field(..., description="Context or description around the table")

class ExtractedImage(BaseModel):
    """Model for extracted image information"""
    description: str = Field(..., description="Description of the image content")
    type: str = Field(..., description="Type of image (chart, graph, logo, diagram, etc.)")
    page_number: int = Field(..., description="Page number where image was found")
    key_insights: List[str] = Field(default_factory=list, description="Key insights from the image")
    data_points: Dict[str, Any] = Field(default_factory=dict, description="Extracted data points if applicable")

class ExtractedSection(BaseModel):
    """Model for extracted document sections"""
    title: str = Field(..., description="Section title")
    content: str = Field(..., description="Section content")
    page_number: int = Field(..., description="Page number where section starts")
    key_points: List[str] = Field(default_factory=list, description="Key points from this section")

class FinancialMetrics(BaseModel):
    """Model for extracted financial metrics"""
    revenue: Optional[str] = Field(..., description="Revenue figures mentioned")
    profit: Optional[str] = Field(..., description="Profit/loss figures")
    growth_rate: Optional[str] = Field(..., description="Growth rate percentages")
    funding_raised: Optional[str] = Field(..., description="Funding amounts raised")
    valuation: Optional[str] = Field(..., description="Company valuation")
    burn_rate: Optional[str] = Field(..., description="Monthly/yearly burn rate")
    runway: Optional[str] = Field(..., description="Financial runway")
    other_metrics: Dict[str, str] = Field(default_factory=dict, description="Other financial metrics found")

class CompanyInfo(BaseModel):
    """Model for extracted company information"""
    company_name: Optional[str] = Field(..., description="Company name")
    industry: Optional[str] = Field(..., description="Industry or sector")
    founded_year: Optional[int] = Field(..., description="Year company was founded")
    location: Optional[str] = Field(..., description="Company location/headquarters")
    stage: Optional[str] = Field(..., description="Business stage (startup, growth, etc.)")
    employees: Optional[str] = Field(..., description="Number of employees")
    website: Optional[str] = Field(..., description="Company website")
    description: Optional[str] = Field(..., description="Company description/mission")

class MarketInfo(BaseModel):
    """Model for extracted market information"""
    market_size: Optional[str] = Field(..., description="Total addressable market size")
    target_market: Optional[str] = Field(..., description="Target market description")
    market_opportunity: Optional[str] = Field(..., description="Market opportunity description")
    competitors: List[str] = Field(default_factory=list, description="List of competitors mentioned")
    competitive_advantage: Optional[str] = Field(..., description="Competitive advantages")
    customer_segments: List[str] = Field(default_factory=list, description="Customer segments")

class TeamInfo(BaseModel):
    """Model for extracted team information"""
    founders: List[str] = Field(default_factory=list, description="Founder names and backgrounds")
    key_team_members: List[str] = Field(default_factory=list, description="Key team members")
    advisors: List[str] = Field(default_factory=list, description="Advisors and board members")
    team_size: Optional[str] = Field(..., description="Total team size")
    key_hires: List[str] = Field(default_factory=list, description="Key hires or positions to fill")

class BusinessModel(BaseModel):
    """Model for extracted business model information"""
    revenue_model: Optional[str] = Field(..., description="How the company makes money")
    pricing_strategy: Optional[str] = Field(..., description="Pricing strategy")
    customer_acquisition: Optional[str] = Field(..., description="Customer acquisition strategy")
    distribution_channels: List[str] = Field(default_factory=list, description="Distribution channels")
    partnerships: List[str] = Field(default_factory=list, description="Key partnerships")
    scalability: Optional[str] = Field(..., description="Business scalability factors")

class TractionMetrics(BaseModel):
    """Model for extracted traction metrics"""
    customers: Optional[str] = Field(..., description="Number of customers")
    users: Optional[str] = Field(..., description="Number of users")
    revenue_growth: Optional[str] = Field(..., description="Revenue growth metrics")
    user_growth: Optional[str] = Field(..., description="User growth metrics")
    retention_rate: Optional[str] = Field(..., description="Customer retention rate")
    key_metrics: Dict[str, str] = Field(default_factory=dict, description="Other key traction metrics")
    milestones: List[str] = Field(default_factory=list, description="Key milestones achieved")

class RiskFactors(BaseModel):
    """Model for extracted risk factors"""
    market_risks: List[str] = Field(default_factory=list, description="Market-related risks")
    operational_risks: List[str] = Field(default_factory=list, description="Operational risks")
    financial_risks: List[str] = Field(default_factory=list, description="Financial risks")
    regulatory_risks: List[str] = Field(default_factory=list, description="Regulatory risks")
    competitive_risks: List[str] = Field(default_factory=list, description="Competitive risks")
    technology_risks: List[str] = Field(default_factory=list, description="Technology risks")
    other_risks: List[str] = Field(default_factory=list, description="Other identified risks")

class FundingInfo(BaseModel):
    """Model for extracted funding information"""
    funding_amount: Optional[str] = Field(..., description="Amount of funding being raised")
    use_of_funds: List[str] = Field(default_factory=list, description="How funds will be used")
    previous_funding: List[str] = Field(default_factory=list, description="Previous funding rounds")
    investors: List[str] = Field(default_factory=list, description="Current/previous investors")
    equity_offered: Optional[str] = Field(..., description="Equity percentage offered")
    valuation: Optional[str] = Field(..., description="Pre/post money valuation")

class DocumentMetadata(BaseModel):
    """Model for document metadata"""
    total_pages: int = Field(..., description="Total number of pages")
    document_type: str = Field(default="pitch_deck", description="Type of document")
    creation_date: Optional[datetime] = Field(..., description="Document creation date")
    last_modified: Optional[datetime] = Field(..., description="Last modification date")
    quality_score: float = Field(..., ge=0, le=1, description="Quality of content extraction (0-1)")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence in extraction accuracy (0-1)")

class PDFExtractionResult(BaseModel):
    """Complete PDF extraction result model"""
    # Document structure
    full_text: str = Field(..., description="Complete extracted text from all pages")
    sections: List[ExtractedSection] = Field(default_factory=list, description="Identified sections")
    tables: List[ExtractedTable] = Field(default_factory=list, description="Extracted tables")
    images: List[ExtractedImage] = Field(default_factory=list, description="Analyzed images")
    
    # Business information
    company_info: CompanyInfo = Field(default_factory=CompanyInfo, description="Company information")
    market_info: MarketInfo = Field(default_factory=MarketInfo, description="Market information")
    team_info: TeamInfo = Field(default_factory=TeamInfo, description="Team information")
    business_model: BusinessModel = Field(default_factory=BusinessModel, description="Business model")
    
    # Financial and traction data
    financial_metrics: FinancialMetrics = Field(default_factory=FinancialMetrics, description="Financial metrics")
    traction_metrics: TractionMetrics = Field(default_factory=TractionMetrics, description="Traction metrics")
    funding_info: FundingInfo = Field(default_factory=FundingInfo, description="Funding information")
    
    # Risk assessment
    risk_factors: RiskFactors = Field(default_factory=RiskFactors, description="Identified risk factors")
    
    # Metadata
    metadata: DocumentMetadata = Field(..., description="Document metadata and quality metrics")
    
    # Additional insights
    key_insights: List[str] = Field(default_factory=list, description="Key insights from the document")
    missing_information: List[str] = Field(default_factory=list, description="Important information that appears to be missing")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations for improving the pitch deck")

class ExtractionError(BaseModel):
    """Model for extraction errors"""
    error_type: str = Field(..., description="Type of error")
    error_message: str = Field(..., description="Error message")
    page_number: Optional[int] = Field(..., description="Page number where error occurred")
    timestamp: datetime = Field(default_factory=datetime.now, description="When the error occurred")