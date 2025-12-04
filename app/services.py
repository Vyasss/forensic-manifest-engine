import os
import numpy as np
from dotenv import load_dotenv
from .forensics.ela_analyzer import get_ela_score
from .forensics.frequency_analyzer import get_frequency_score
from .forensics.prnu_analyzer import get_prnu_score
from .ai.gemini_vlm import get_vlm_reasoning_score

load_dotenv()

FIXED_AI_THRESHOLD = 0.19

def analyze_image_forensics(image_path: str) -> dict:
    """Multi-signal forensic analysis."""
    
    scores = {}
    
    # 1. ELA (Robust VoV)
    try:
        scores['ela'] = get_ela_score(image_path)
    except Exception as e:
        scores['ela'] = 0.0
    
    # 2. Frequency
    try:
        scores['frequency'] = get_frequency_score(image_path)
    except Exception as e:
        scores['frequency'] = 0.0
    
    # 3. PRNU
    try:
        scores['prnu'] = get_prnu_score(image_path)
    except Exception as e:
        scores['prnu'] = 0.0
    
    # 4. VLM (Visual Reasoning)
    scores['vlm'] = get_vlm_reasoning_score(image_path)
    
    # Extract final scores
    ela_score = float(scores.get('ela', 0.0))
    freq_score = float(scores.get('frequency', 0.0))
    prnu_score = float(scores.get('prnu', 0.0))
    vlm_score = float(scores.get('vlm', 0.0))
    
    P_fraud = 0.0
    
    if vlm_score > 0.0: 
        # Case A: VLM is available and returning an explicit score (standard operation)
        P_fraud = (
            vlm_score * 0.80 +        
            freq_score * 0.10 +       
            prnu_score * 0.05 +
            ela_score * 0.05
        )
    else:  
        P_fraud = (
            freq_score * 0.40 +
            prnu_score * 0.35 +
            ela_score * 0.25
        )
    
    print(f"P(Synthetic)={P_fraud:.3f} (ELA:{ela_score:.3f}, PRNU:{prnu_score:.3f}, VLM:{vlm_score:.3f})")
    
    return {
        'P_fraud': round(P_fraud, 3),
        'breakdown': scores,
        'confidence': calculate_confidence(scores, vlm_score)
    }


def calculate_confidence(scores: dict, vlm_score: float) -> float:
    """Calculate confidence based on signal availability and agreement."""
    
    # If VLM is available and returned an explicit score, confidence is based on VLM's availability.
    if vlm_score > 0.1:
        return 0.80
    
    # VLM unavailable or explicitly low (0.1) means lower confidence.
    else:
        active_scores = [v for v in scores.values() if v > 0.0]
        if len(active_scores) < 2:
            return 0.30
        variance = np.var(active_scores)
        agreement = 1.0 - min(variance * 3, 1.0)
        return round(0.30 + (agreement * 0.20), 2)


def check_ai_status(image_path: str) -> dict:
    """
    Determines if an image is AI-generated (synthetic) or not.
    """
    
    forensics = analyze_image_forensics(image_path)
    P_synthetic = forensics['P_fraud']
    
    # Simple threshold: 0.5
    threshold = 0.5
    
    if P_synthetic > threshold:
        decision = "AI_GENERATED"
        reasoning = f"P(Synthetic)={P_synthetic:.3f} > {threshold}. Image shows signs of AI generation."
    else:
        decision = "REAL_PHOTO"
        reasoning = f"P(Synthetic)={P_synthetic:.3f} ≤ {threshold}. Image appears to be a real photograph."
    
    # Ensure all values are proper floats for Pydantic validation
    return {
        'decision': decision,
        'reasoning': reasoning,
        'P_synthetic': float(P_synthetic),
        'forensics_breakdown': {
            'ela': float(forensics['breakdown'].get('ela', 0.0)),
            'frequency': float(forensics['breakdown'].get('frequency', 0.0)),
            'prnu': float(forensics['breakdown'].get('prnu', 0.0)),
            'vlm': float(forensics['breakdown'].get('vlm', 0.0))
        },
        'confidence': float(forensics['confidence'])
    }



def check_fraud_complete(user_id: str, image_path: str) -> dict:
    """Complete fraud check pipeline."""
    
    # This function is not used in the simplified AI checker but kept for compatibility.
    profile = {} 
    T_threshold = 0.5 
    
    forensics = analyze_image_forensics(image_path)
    P_fraud = forensics['P_fraud']
    
    if P_fraud > T_threshold:
        decision = "REJECT"
        reasoning = f"P(Fraud)={P_fraud:.3f} > T={T_threshold:.4f}. Claim rejected due to high fraud risk."
    else:
        decision = "APPROVE"
        reasoning = f"P(Fraud)={P_fraud:.3f} ≤ T={T_threshold:.4f}. Claim approved."
    
    return {
        'user_id': user_id,
        'decision': decision,
        'reasoning': reasoning,
        'P_fraud': P_fraud,
        'T_threshold': T_threshold,
        'forensics_breakdown': forensics['breakdown'],
        'confidence': forensics['confidence']
    }