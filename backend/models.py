from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from enum import Enum

class ChatRequest(BaseModel):
    message: str
    max_steps: Optional[int] = 15

class ChatResponse(BaseModel):
    answer: str
    trace: List[Dict[str, Any]]

class InvestmentHorizon(str, Enum):
    short_term = "short-term"
    medium_term = "medium-term"
    long_term = "long-term"

class RiskTolerance(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

class InvestmentGoals(str, Enum):
    growth = "growth"
    income = "income"
    preservation = "preservation"

class LiquidityNeeds(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"

class InvestmentProficiency(str, Enum):
    novice = "novice"
    informed = "informed"
    advanced = "advanced"

class UserProfile(BaseModel):
    investment_horizon: InvestmentHorizon
    risk_tolerance: RiskTolerance
    investment_goals: InvestmentGoals
    investment_proficiency: InvestmentProficiency
    liquidity_needs: LiquidityNeeds