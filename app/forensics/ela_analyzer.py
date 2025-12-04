from PIL import Image, ImageChops
import os
import numpy as np
import tempfile

ELA_QUALITY = 90
PATCH_SIZE = 64 
MIN_SCORE_FLOOR = 0.005 

def calculate_ela_patch_variances(diff_array: np.ndarray) -> tuple[float, float, float]:
    """Calculates the Variance of Variances (VoV) across the ELA difference map."""
    # Ensure the array is 3D (H, W, Channels)
    if diff_array.ndim == 2:
        diff_array = np.expand_dims(diff_array, axis=2)
    
    h, w, _ = diff_array.shape
    variances = []
    
    mean_error = float(np.mean(diff_array))
    
    # Core VoV Calculation
    for i in range(0, h - PATCH_SIZE + 1, PATCH_SIZE):
        for j in range(0, w - PATCH_SIZE + 1, PATCH_SIZE):
            patch = diff_array[i:i + PATCH_SIZE, j:j + PATCH_SIZE]
            if patch.size > 0:
                variances.append(np.var(patch))
    
    if len(variances) < 2:
        return 0.0, 0.0, mean_error 
    
    overall_variance = np.var(diff_array)
    ela_vov = np.var(variances)
    
    return overall_variance, ela_vov, mean_error


def get_ela_score(image_path: str) -> float:
    """Performs ELA and returns a fraud score."""
    
    fd, temp_path = tempfile.mkstemp(suffix='.jpg')
    os.close(fd)
    
    try:
        original = Image.open(image_path).convert('RGB')
        original.save(temp_path, 'JPEG', quality=ELA_QUALITY)
        recompressed = Image.open(temp_path).convert('RGB')
        
        # Calculate difference map
        diff = ImageChops.difference(original, recompressed)
        diff_array = np.array(diff)
        
        # Calculate core metrics
        overall_variance, ela_vov, mean_error = calculate_ela_patch_variances(diff_array)
        max_diff = float(np.max(diff_array))

        
        if ela_vov < 100: vov_score = 0.0
        elif ela_vov < 300: vov_score = (ela_vov - 100) / 400
        else: vov_score = min(0.5 + (ela_vov - 300) / 800, 1.0)
            
        
        if mean_error < 15: mean_score = 0.0
        elif mean_error < 40: mean_score = (mean_error - 15) / 50
        else: mean_score = min(0.5 + (mean_error - 40) / 80, 1.0)
        
        # Combined score (weighted)
        score = (vov_score * 0.60 + mean_score * 0.25 + (min(max_diff / 255, 1.0) * 0.15))
        
        
        if vov_score > 0.4:
            # If strong non-uniform manipulation is detected, boost the final score aggressively.
            score = min(1.0, score + 0.35)
        elif mean_error > 50 and vov_score < 0.1:
            # Dampen score for real, heavily compressed images
            score = score * 0.25
            
        return round(max(score, MIN_SCORE_FLOOR), 3) # Apply the floor
        
    except Exception as e:
        # If the ELA logic fails, return the floor score to avoid 0.0
        return MIN_SCORE_FLOOR 

    finally:
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        except:
            pass