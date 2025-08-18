from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class FinancialMetrics(BaseModel):
    """Model for extracted financial metrics"""
    revenue: str = Field(..., description="Revenue figures mentioned/ 'N/A' if not mentioned")
    profit: str = Field(..., description="Profit/loss figures/ 'N/A' if not mentioned")
    growth_rate: str = Field(..., description="Growth rate percentages/ 'N/A' if not mentioned")
    funding_raised: str = Field(..., description="Funding amounts raised/ 'N/A' if not mentioned")
    valuation: str = Field(..., description="Company valuation/ 'N/A' if not mentioned")
    burn_rate: str = Field(..., description="Monthly/yearly burn rate/ 'N/A' if not mentioned")
    runway: str = Field(..., description="Financial runway/ 'N/A' if not mentioned")
    other_metrics: str = Field(..., description="Other financial metrics found/ 'N/A' if not mentioned")

class CompanyInfo(BaseModel):
    """Model for extracted company information"""
    company_name: str = Field(..., description="Company name/ 'N/A' if not mentioned")
    industry: str = Field(..., description="Industry or sector/ 'N/A' if not mentioned")
    founded_year: int = Field(..., description="Year company was founded/ 'N/A' if not mentioned")
    location: str = Field(..., description="Company location/headquarters/ 'N/A' if not mentioned")
    stage: str = Field(..., description="Business stage (startup, growth, etc.)/ 'N/A' if not mentioned")
    employees: str = Field(..., description="Number of employees/ 'N/A' if not mentioned")
    website: str = Field(..., description="Company website/ 'N/A' if not mentioned")
    description: str = Field(..., description="Company description/mission/ 'N/A' if not mentioned")

class MarketInfo(BaseModel):
    """Model for extracted market information"""
    market_size: str = Field(..., description="Total addressable market size/ 'N/A' if not mentioned")
    target_market: str = Field(..., description="Target market description/ 'N/A' if not mentioned")
    market_opportunity: str = Field(..., description="Market opportunity description/ 'N/A' if not mentioned")
    competitors: List[str] = Field(..., description="List of competitors mentioned")
    competitive_advantage: str = Field(..., description="Competitive advantages/ 'N/A' if not mentioned")
    customer_segments: List[str] = Field(..., description="Customer segments")

class TeamInfo(BaseModel):
    """Model for extracted team information"""
    founders: List[str] = Field(..., description="Founder names and backgrounds")
    key_team_members: List[str] = Field(..., description="Key team members")
    advisors: List[str] = Field(..., description="Advisors and board members")
    team_size: str = Field(..., description="Total team size/ 'N/A' if not mentioned")
    key_hires: List[str] = Field(..., description="Key hires or positions to fill")

class BusinessModel(BaseModel):
    """Model for extracted business model information"""
    revenue_model: str = Field(..., description="How the company makes money/ 'N/A' if not mentioned")
    pricing_strategy: str = Field(..., description="Pricing strategy/ 'N/A' if not mentioned")
    customer_acquisition: str = Field(..., description="Customer acquisition strategy/ 'N/A' if not mentioned")
    distribution_channels: List[str] = Field(..., description="Distribution channels")
    partnerships: List[str] = Field(..., description="Key partnerships")
    scalability: str = Field(..., description="Business scalability factors/ 'N/A' if not mentioned")

class TractionMetrics(BaseModel):
    """Model for extracted traction metrics"""
    customers: str = Field(..., description="Number of customers/ 'N/A' if not mentioned")
    users: str = Field(..., description="Number of users/ 'N/A' if not mentioned")
    revenue_growth: str = Field(..., description="Revenue growth metrics/ 'N/A' if not mentioned")
    user_growth: str = Field(..., description="User growth metrics/ 'N/A' if not mentioned")
    retention_rate: str = Field(..., description="Customer retention rate/ 'N/A' if not mentioned")
    key_metrics: str = Field(..., description="Other key traction metrics/ 'N/A' if not mentioned")
    milestones: List[str] = Field(..., description="Key milestones achieved")

class RiskFactors(BaseModel):
    """Model for extracted risk factors"""
    market_risks: List[str] = Field(..., description="Market-related risks")
    operational_risks: List[str] = Field(..., description="Operational risks")
    financial_risks: List[str] = Field(..., description="Financial risks")
    regulatory_risks: List[str] = Field(..., description="Regulatory risks")
    competitive_risks: List[str] = Field(..., description="Competitive risks")
    technology_risks: List[str] = Field(..., description="Technology risks")
    other_risks: List[str] = Field(..., description="Other identified risks")

class FundingInfo(BaseModel):
    """Model for extracted funding information"""
    funding_amount: str = Field(..., description="Amount of funding being raised/ 'N/A' if not mentioned")
    use_of_funds: List[str] = Field(..., description="How funds will be used")
    previous_funding: List[str] = Field(..., description="Previous funding rounds")
    investors: List[str] = Field(..., description="Current/previous investors")
    equity_offered: str = Field(..., description="Equity percentage offered/ 'N/A' if not mentioned")
    valuation: str = Field(..., description="Pre/post money valuation/ 'N/A' if not mentioned")

class PDFExtractionResult(BaseModel):
    """Complete PDF extraction result model"""
    
    # Business information
    company_info: CompanyInfo = Field(..., description="Company information")
    market_info: MarketInfo = Field(..., description="Market information")
    team_info: TeamInfo = Field(..., description="Team information")
    business_model: BusinessModel = Field(..., description="Business model")
    
    # Financial and traction data
    financial_metrics: FinancialMetrics = Field(..., description="Financial metrics")
    traction_metrics: TractionMetrics = Field(..., description="Traction metrics")
    funding_info: FundingInfo = Field(..., description="Funding information")
    
    # Risk assessment
    risk_factors: RiskFactors = Field(..., description="Identified risk factors")
    
    # Additional insights
    recommendations: List[str] = Field(..., description="Recommendations for improving the pitch deck")

class ExtractionError(BaseModel):
    """Model for extraction errors"""
    error_type: str = Field(..., description="Type of error")
    error_message: str = Field(..., description="Error message")
    page_number: Optional[int] = Field(..., description="Page number where error occurred")
    timestamp: datetime = Field(default_factory=datetime.now, description="When the error occurred")