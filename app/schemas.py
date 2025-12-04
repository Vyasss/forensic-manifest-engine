from pydantic import BaseModel, Field
from typing import Dict, Optional

class AIServiceResponse(BaseModel):
    decision: str = Field(..., description="AI_GENERATED or REAL_PHOTO")
    reasoning: str
    P_synthetic: float = Field(..., ge=0.0, le=1.0)
    forensics_breakdown: Dict[str, float]
    confidence: float = Field(..., ge=0.0, le=1.0)