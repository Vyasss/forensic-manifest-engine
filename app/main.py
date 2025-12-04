from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import os
import tempfile
import shutil
import webbrowser
from threading import Timer

from app.services import check_ai_status 
from app.schemas import AIServiceResponse # Assuming the schema is updated

app = FastAPI(title="Forensic Manifest") 

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Forensic Manifest</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #4ba276 0%, #667eea 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 20px;
            padding: 40px;
            max-width: 600px;
            width: 100%;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 { text-align: center; color: #333; margin-bottom: 10px; font-size: 32px; }
        .subtitle { text-align: center; color: #666; margin-bottom: 30px; font-size: 14px; }
        .form-group { margin-bottom: 25px; }
        label { display: block; margin-bottom: 8px; color: #333; font-weight: 600; font-size: 14px; }
        .file-input-wrapper { position: relative; overflow: hidden; width: 100%; }
        .file-input-wrapper input[type="file"] { position: absolute; left: -9999px; }
        .file-input-label {
            display: block;
            padding: 20px;
            border: 2px dashed #4ba276;
            border-radius: 8px;
            text-align: center;
            cursor: pointer;
            background: #f8fff8;
            transition: all 0.3s;
        }
        .file-input-label:hover { background: #4ba276; color: white; }
        .file-name { margin-top: 10px; font-size: 14px; color: #666; text-align: center; }
        button {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #4ba276 0%, #667eea 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }
        button:hover:not(:disabled) { transform: translateY(-2px); }
        button:disabled { opacity: 0.6; cursor: not-allowed; }
        .loader { text-align: center; padding: 20px; display: none; }
        .loader.show { display: block; }
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #4ba276;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .result { margin-top: 30px; padding: 20px; border-radius: 8px; display: none; }
        .result.show { display: block; }
        .result.real { background: #d4edda; border: 2px solid #28a745; }
        .result.ai { background: #f8d7da; border: 2px solid #dc3545; }
        .result-title { font-size: 20px; font-weight: 700; margin-bottom: 10px; }
        .result-details { font-size: 14px; line-height: 1.6; margin-bottom: 15px; }
        .forensics { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 15px; }
        .forensic-item { background: rgba(255,255,255,0.5); padding: 10px; border-radius: 6px; }
        .forensic-label { font-size: 12px; text-transform: uppercase; font-weight: 600; color: #666; }
        .forensic-value { font-size: 24px; font-weight: 700; color: #333; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Forensic Manifest</h1>
        <p class="subtitle">Forensic Analysis for Synthetic Content</p>
        <form id="aiDetectForm">
            <div class="form-group">
                <label for="imageFile">Image File</label>
                <div class="file-input-wrapper">
                    <input type="file" id="imageFile" accept="image/*" required>
                    <label for="imageFile" class="file-input-label">📁 Click to Choose Image</label>
                </div>
                <div class="file-name" id="fileName"></div>
            </div>
            <button type="submit" id="submitBtn"> Analyze Image</button>
        </form>
        <div class="loader" id="loader">
            <div class="spinner"></div>
            <p style="margin-top: 15px; color: #666;">Analyzing with AI forensics...</p>
        </div>
        <div class="result" id="result">
            <div class="result-title" id="resultTitle"></div>
            <div class="result-details" id="resultDetails"></div>
            <div class="forensics" id="forensics"></div>
        </div>
    </div>
    <script>
        const form = document.getElementById('aiDetectForm');
        const fileInput = document.getElementById('imageFile');
        const fileName = document.getElementById('fileName');
        const loader = document.getElementById('loader');
        const result = document.getElementById('result');
        const submitBtn = document.getElementById('submitBtn');
        
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                fileName.textContent = 'Selected: ' + e.target.files[0].name;
            }
        });
        
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData();
            formData.append('image', fileInput.files[0]);
            loader.classList.add('show');
            result.classList.remove('show');
            submitBtn.disabled = true;
            try {
                // NOTE: We use the new endpoint
                const response = await fetch('/api/v1/ai-check', { method: 'POST', body: formData });
                if (!response.ok) throw new Error('HTTP error! status: ' + response.status);
                const data = await response.json();
                loader.classList.remove('show');
                submitBtn.disabled = false;
                displayResult(data);
            } catch (error) {
                loader.classList.remove('show');
                submitBtn.disabled = false;
                alert('Error: ' + error.message);
            }
        });
        
        function displayResult(data) {
            result.classList.add('show');
            result.className = 'result show';
            // NOTE: Decision field is now AI_GENERATED or REAL_PHOTO
            if (data.decision === 'REAL_PHOTO') result.classList.add('real');
            else if (data.decision === 'AI_GENERATED') result.classList.add('ai');

            const emoji = data.decision === 'REAL_PHOTO' ? '✅' : '❌';
            const title = data.decision.replace('_', ' ');
            document.getElementById('resultTitle').textContent = emoji + ' ' + title;
            document.getElementById('resultDetails').innerHTML = '<strong>Reasoning:</strong> ' + data.reasoning + '<br><br>' +
                '<strong>P(Synthetic):</strong> ' + (data.P_synthetic * 100).toFixed(1) + '%<br>' +
                '<strong>Confidence:</strong> ' + (data.confidence * 100).toFixed(1) + '%';
            document.getElementById('forensics').innerHTML = 
                '<div class="forensic-item"><div class="forensic-label">ELA</div><div class="forensic-value">' + 
                (data.forensics_breakdown.ela * 100).toFixed(0) + '%</div></div>' +
                '<div class="forensic-item"><div class="forensic-label">Frequency</div><div class="forensic-value">' + 
                (data.forensics_breakdown.frequency * 100).toFixed(0) + '%</div></div>' +
                '<div class="forensic-item"><div class="forensic-label">PRNU</div><div class="forensic-value">' + 
                (data.forensics_breakdown.prnu * 100).toFixed(0) + '%</div></div>' +
                '<div class="forensic-item"><div class="forensic-label">VLM</div><div class="forensic-value">' + 
                (data.forensics_breakdown.vlm * 100).toFixed(0) + '%</div></div>';
        }
    </script>
</body>
</html>"""

@app.get("/", response_class=HTMLResponse)
async def root():
    return HTML_TEMPLATE


@app.post("/api/v1/ai-check", response_model=AIServiceResponse)
async def check_ai_image(image: UploadFile = File(...)):
    if not image.content_type.startswith('image/'):
        raise HTTPException(400, "File must be an image")
    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
        shutil.copyfileobj(image.file, tmp)
        tmp_path = tmp.name
    try:
        
        result = check_ai_status(tmp_path)
        return result
    finally:
        
        try:
            os.remove(tmp_path)
        except OSError as e:
            # Ignore file not found errors if the file was already cleaned up
            if e.errno != 2: # 2 is ENOENT (No such file or directory)
                print(f" Warning: Could not delete temp file {tmp_path}: {e}")

def open_browser():
    webbrowser.open("http://127.0.0.1:8000")

@app.on_event("startup")
async def startup_event():
    Timer(1.0, open_browser).start()
    print("\n Server started! Opening browser...")
    print(" API Docs: http://127.0.0.1:8000/docs")
    print(" Frontend: http://127.0.0.1:8000\n")