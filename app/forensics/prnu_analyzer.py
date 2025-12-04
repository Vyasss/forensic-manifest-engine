import cv2
import numpy as np

def get_prnu_score(image_path: str) -> float:
    """
    PRNU with better handling of compressed images.
    """
    
    img = cv2.imread(image_path)
    if img is None:
        print(" PRNU: Failed to load image")
        return 0.5
        
    # Denoise
    denoised = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)
    noise = img.astype(float) - denoised.astype(float)
    noise_gray = cv2.cvtColor(np.abs(noise).astype(np.uint8), cv2.COLOR_BGR2GRAY)
    
    # Calculate VoV
    h, w = noise_gray.shape
    patch_size = 64
    variances = []
    
    for i in range(0, h - patch_size + 1, patch_size):
        for j in range(0, w - patch_size + 1, patch_size):
            patch = noise_gray[i:i + patch_size, j:j + patch_size]
            if patch.size > 0:
                variances.append(np.var(patch))
    
    if len(variances) < 2:
        print("  PRNU: Not enough patches")
        return 0.5
        
    variance_of_variances = np.var(variances)
    
    print(f" PRNU Raw VoV: {variance_of_variances:.2f}")
    
    
    
    if variance_of_variances < 20:
        score = 0.0  # Definitely real
    elif variance_of_variances < 60:
        # Likely real but compressed
        score = (variance_of_variances - 20) / 200  
    elif variance_of_variances < 100:
        # Borderline
        score = 0.2 + (variance_of_variances - 60) / 100  # 0.2-0.6
    else:
        # Very likely AI
        score = min(0.6 + (variance_of_variances - 100) / 200, 1.0)
    
    print(f" PRNU Score: {score:.3f}")
    
    return round(score, 3)