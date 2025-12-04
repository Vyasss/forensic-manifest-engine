import cv2
import numpy as np
from scipy import fftpack

MIN_SCORE_FLOOR = 0.005

def get_frequency_score(image_path: str) -> float:
    """Analyze frequency domain with better compression handling."""
    
    # --- SAFETY CHECK 1: Ensure image loads ---
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return 0.80 # High fallback score if file can't be read
    
    
    if img.shape[0] < 50 or img.shape[1] < 50:
        return 0.80

    try:
        # Apply 2D FFT
        fft = fftpack.fft2(img)
        fft_shifted = fftpack.fftshift(fft)
        magnitude = np.abs(fft_shifted)
        
        h, w = magnitude.shape
        center = (h//2, w//2)
        
        # Sample frequency bands
        high_freq = magnitude[center[0]-10:center[0]+10, center[1]+w//4:center[1]+w//3]
        low_freq = magnitude[center[0]-20:center[0]+20, center[1]-20:center[1]+20]
        
        if high_freq.size == 0 or low_freq.size == 0:
            return 0.80

        # Calculate ratio
        ratio = np.mean(high_freq) / (np.mean(low_freq) + 1e-6)
        
        print(f"📊 Frequency Ratio: {ratio:.3f}")
        
        # --- NORMALIZATION ---
        if ratio < 0.25:
            score = 0.0
        elif ratio < 0.45:
            score = (ratio - 0.25) / 0.40
        else:
            score = 0.5 + min((ratio - 0.45) / 0.50, 0.5)
        
        return round(max(score, MIN_SCORE_FLOOR), 3) # Apply the floor

    except Exception as e:
        # Final high fallback score on internal error
        return 0.80