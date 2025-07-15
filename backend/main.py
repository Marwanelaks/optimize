import os
import io
import zipfile
import tempfile
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any
import re
from openai import OpenAI
from fastapi import FastAPI, UploadFile, File, HTTPException, Query, BackgroundTasks, Response, Request, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import htmlmin
from csscompressor import compress as css_compress
from jsmin import jsmin
from PIL import Image
import requests
import subprocess
from bs4 import BeautifulSoup
import sass
import json
from datetime import datetime
import hashlib
import logging
from pydantic import BaseModel
import concurrent.futures

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Website Optimizer API",
    description="Backend for AI-powered website optimization tool",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
TEMP_DIR = os.getenv("TEMP_DIR", "/tmp/optimizer")
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
os.makedirs(TEMP_DIR, exist_ok=True)

# Pydantic models
class OptimizationRequest(BaseModel):
    aggressive: bool = False
    seo_focus: bool = True
    accessibility_focus: bool = True

class OptimizationResponse(BaseModel):
    download_url: str
    report: Dict[str, Any]
    message: str

class AIAnalysisRequest(BaseModel):
    prompt: str
    code: Optional[str] = None
    file_type: Optional[str] = None

class FileConversionRequest(BaseModel):
    target_format: str
    content: Optional[str] = None

# AI Optimization Client
class AIOptimizer:
    def __init__(self):
        self.client = OpenAI(
            api_key="",
            base_url="https://openrouter.ai/api/v1/"
        )
    
    def optimize_code(self, code: str, file_type: str) -> str:
        """Optimize code with AI context-awareness"""
        prompt = f"""
        Optimize this {file_type} code for performance, accessibility, and SEO.
        Apply these specific optimizations:
        1. Minify the code without breaking functionality
        2. Add lazy loading where appropriate
        3. Suggest accessibility improvements
        4. Apply modern best practices
        5. Add schema.org markup if HTML
        6. Optimize critical CSS path if CSS
        
        Return ONLY the optimized code, no explanations.
        
        Original code:
        {code}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="deepseek/deepseek-chat-v3-0324:free",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"AI optimization failed: {str(e)}")
            return code

    def analyze_code(self, code: str, file_type: str) -> Dict[str, Any]:
        """Analyze code and return metrics and suggestions"""
        prompt = f"""
        Analyze this {file_type} code and provide:
        1. Performance score (0-100)
        2. SEO score (0-100) if HTML
        3. Accessibility score (0-100)
        4. 3 specific optimization suggestions
        5. Estimated optimization potential (0-100%)
        6. Code complexity analysis
        7. Best practice compliance
        
        Return as JSON with these keys:
        - performance_score
        - seo_score (if applicable)
        - accessibility_score
        - suggestions
        - optimization_potential
        - complexity_analysis
        - best_practice_compliance
        """
        
        try:
            response = self.client.chat.completions.create(
                model="deepseek/deepseek-chat-v3-0324:free",
                messages=[{"role": "user", "content": f"{prompt}\n\n{code}"}],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"AI analysis failed: {str(e)}")
            return {
                "performance_score": 50,
                "seo_score": 50,
                "accessibility_score": 50,
                "suggestions": ["Analysis failed"],
                "optimization_potential": 0,
                "complexity_analysis": "Unknown",
                "best_practice_compliance": "Unknown"
            }

    def convert_code(self, code: str, source_format: str, target_format: str) -> str:
        """Convert code between formats using AI"""
        prompt = f"""
        Convert the following {source_format} code to {target_format}.
        Maintain all functionality while following {target_format} best practices.
        Include all necessary imports/dependencies.
        Return ONLY the converted code, no explanations.
        
        {source_format} code:
        {code}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="deepseek/deepseek-chat-v3-0324:free",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"AI conversion failed: {str(e)}")
            return code

ai_optimizer = AIOptimizer()

def get_file_hash(file_path: str) -> str:
    """Generate hash of file contents"""
    with open(file_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def analyze_file(file_path: str) -> Dict[str, Any]:
    """Analyze a single file"""
    try:
        file_type = Path(file_path).suffix[1:].lower()
        file_size = os.path.getsize(file_path)
        file_hash = get_file_hash(file_path)
        
        # Skip analysis for binary files
        if file_type in ('png', 'jpg', 'jpeg', 'gif', 'webp', 'ico', 'svg'):
            return {
                "path": file_path,
                "type": file_type,
                "size": file_size,
                "hash": file_hash,
                "analysis": None,
                "optimized": False,
                "optimized_size": None,
                "optimized_hash": None,
                "optimized_analysis": None
            }
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        analysis = ai_optimizer.analyze_code(content, file_type)
        
        return {
            "path": file_path,
            "type": file_type,
            "size": file_size,
            "hash": file_hash,
            "analysis": analysis,
            "optimized": False,
            "optimized_size": None,
            "optimized_hash": None,
            "optimized_analysis": None
        }
    except Exception as e:
        logger.error(f"Error analyzing {file_path}: {str(e)}")
        return {
            "path": file_path,
            "type": Path(file_path).suffix[1:].lower(),
            "size": os.path.getsize(file_path),
            "hash": get_file_hash(file_path),
            "analysis": None,
            "optimized": False,
            "optimized_size": None,
            "optimized_hash": None,
            "optimized_analysis": None
        }

def optimize_image(image_path: str, aggressive: bool = False) -> str:
    """Optimize image and convert to WebP format using AI suggestions"""
    try:
        with Image.open(image_path) as img:
            # Get AI suggestions for image optimization
            analysis_prompt = f"""
            Analyze this image and suggest optimization parameters:
            - Format (WebP/AVIF/JPEG/PNG)
            - Quality level (1-100)
            - Compression method
            - Should we preserve transparency?
            - Recommended dimensions
            
            Current format: {img.format}
            Dimensions: {img.size}
            Mode: {img.mode}
            """
            
            try:
                response = ai_optimizer.optimize_code(analysis_prompt, "image_analysis")
                suggestions = json.loads(response)
                
                # Apply AI suggestions
                format = suggestions.get('format', 'WEBP').upper()
                quality = suggestions.get('quality', 85 if aggressive else 90)
                method = suggestions.get('method', 6)
                preserve_transparency = suggestions.get('preserve_transparency', 
                                                     img.mode in ('RGBA', 'LA') or 
                                                     (img.mode == 'P' and 'transparency' in img.info))
                
                # Convert to recommended format
                new_path = f"{os.path.splitext(image_path)[0]}.{format.lower()}"
                
                if format == 'WEBP':
                    img.save(new_path, 'WEBP', quality=quality, lossless=False, method=method)
                elif format == 'JPEG':
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    img.save(new_path, 'JPEG', quality=quality, optimize=True)
                elif format == 'PNG':
                    img.save(new_path, 'PNG', optimize=True)
                
                # Remove original image
                os.remove(image_path)
                return new_path
                
            except Exception as ai_error:
                logger.warning(f"AI image optimization failed, using default: {str(ai_error)}")
                # Fallback to default WebP conversion
                webp_path = f"{os.path.splitext(image_path)[0]}.webp"
                quality = 75 if aggressive else 85
                
                if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                    img.save(webp_path, 'WEBP', quality=quality, lossless=False, method=6)
                else:
                    img.save(webp_path, 'WEBP', quality=quality, method=6)
                
                os.remove(image_path)
                return webp_path
                
    except Exception as e:
        logger.error(f"Error optimizing image {image_path}: {str(e)}")
        return image_path

def optimize_file(file_path: str, analysis: Dict[str, Any], aggressive: bool = False) -> Dict[str, Any]:
    """Optimize a single file with AI assistance"""
    optimized = analysis.copy()
    
    try:
        file_type = Path(file_path).suffix[1:].lower()
        
        # Handle image optimization
        if file_type in ('png', 'jpg', 'jpeg', 'gif'):
            optimized_path = optimize_image(file_path, aggressive)
            optimized["optimized"] = True
            optimized["optimized_size"] = os.path.getsize(optimized_path)
            optimized["optimized_hash"] = get_file_hash(optimized_path)
            optimized["path"] = optimized_path
            return optimized
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_size = len(content)
        original_content = content
        
        # File type specific optimizations
        if file_type in ('html', 'htm'):
            content = htmlmin.minify(content, 
                                   remove_comments=True, 
                                   remove_empty_space=True,
                                   reduce_boolean_attributes=True)
            content = optimize_external_resources(content)
            if aggressive:
                content = re.sub(r'<script(.*?)>', r'<script\1 defer>', content)
                content = re.sub(r'<link(.*?)>', r'<link\1 fetchpriority="high">', content)
                content = ai_optimizer.optimize_code(content, "HTML")
                
        elif file_type in ('css', 'scss', 'sass'):
            if file_type in ('scss', 'sass'):
                content = sass.compile(string=content)
                new_path = file_path.replace('.scss', '.css').replace('.sass', '.css')
                os.remove(file_path)
                file_path = new_path
            content = css_compress(content)
            if aggressive:
                content = ai_optimizer.optimize_code(content, "CSS")
            
        elif file_type in ('js', 'jsx', 'ts', 'tsx'):
            content = jsmin(content)
            if aggressive:
                content = ai_optimizer.optimize_code(content, "JavaScript")
        
        # Save optimized file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Update optimization results
        optimized["optimized"] = True
        optimized["optimized_size"] = os.path.getsize(file_path)
        optimized["optimized_hash"] = get_file_hash(file_path)
        optimized["optimized_analysis"] = ai_optimizer.analyze_code(content, file_type)
        optimized["path"] = file_path
        
        logger.info(f"Optimized {file_path} from {original_size} to {optimized['optimized_size']} bytes")
        return optimized
        
    except Exception as e:
        logger.error(f"Error optimizing {file_path}: {str(e)}")
        return analysis

def optimize_external_resources(content: str) -> str:
    """Add performance optimizations to external resources"""
    patterns = [
        (r'<script(.*?)src="(.*?)"(.*?)>', r'<script\1src="\2"\3 defer loading="lazy">'),
        (r'<link(.*?)href="(.*?)"(.*?)>', r'<link\1href="\2"\3 loading="lazy">'),
        (r'<iframe(.*?)src="(.*?)"(.*?)>', r'<iframe\1src="\2"\3 loading="lazy">')
    ]
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
    return content

def analyze_seo(directory: str) -> Dict[str, Any]:
    """Analyze and improve SEO for all HTML files using AI"""
    report = {}
    for root, _, files in os.walk(directory):
        for filename in files:
            if filename.lower().endswith(('.html', '.htm')):
                file_path = os.path.join(root, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Get AI SEO analysis
                    analysis = ai_optimizer.analyze_code(content, "HTML")
                    report[file_path] = analysis
                    
                    # Apply AI-generated SEO improvements
                    optimized_content = ai_optimizer.optimize_code(content, "HTML")
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(optimized_content)
                        
                except Exception as e:
                    logger.error(f"Failed to analyze SEO for {file_path}: {str(e)}")
    return report

def process_upload(file: UploadFile, is_github: bool = False, options: OptimizationRequest = None) -> Dict[str, Any]:
    """Process uploaded file or GitHub repo with optimization options"""
    if options is None:
        options = OptimizationRequest()
    
    upload_dir = tempfile.mkdtemp(dir=TEMP_DIR)
    extracted_dir = os.path.join(upload_dir, "extracted")
    os.makedirs(extracted_dir)
    
    try:
        # Handle file upload or GitHub download
        if is_github:
            zip_path = download_github_repo(file, upload_dir)
        else:
            upload_path = os.path.join(upload_dir, file.filename)
            with open(upload_path, 'wb') as f:
                content = file.file.read()
                if len(content) > MAX_FILE_SIZE:
                    raise HTTPException(status_code=400, detail="File too large")
                f.write(content)
            zip_path = upload_path
        
        # Extract files
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extracted_dir)
        
        # Process all files
        results = {
            "files": [],
            "stats": {
                "total_files": 0,
                "optimized_files": 0,
                "total_size_before": 0,
                "total_size_after": 0,
                "start_time": datetime.now().isoformat(),
                "file_types": {},
                "options": options.dict()
            }
        }
        
        # First pass: analyze all files
        for root, _, files in os.walk(extracted_dir):
            for filename in files:
                file_path = os.path.join(root, filename)
                file_analysis = analyze_file(file_path)
                results["files"].append(file_analysis)
                results["stats"]["total_files"] += 1
                results["stats"]["total_size_before"] += file_analysis["size"]
                
                # Track file types
                file_type = file_analysis["type"]
                if file_type not in results["stats"]["file_types"]:
                    results["stats"]["file_types"][file_type] = 0
                results["stats"]["file_types"][file_type] += 1
        
        # Second pass: optimize files in parallel
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for i, file_analysis in enumerate(results["files"]):
                file_path = os.path.join(extracted_dir, file_analysis["path"])
                futures.append(
                    executor.submit(
                        optimize_file,
                        file_path,
                        file_analysis,
                        options.aggressive
                    )
                )
            
            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                optimized = future.result()
                results["files"][i] = optimized
                
                if optimized["optimized"]:
                    results["stats"]["optimized_files"] += 1
                    results["stats"]["total_size_after"] += optimized["optimized_size"]
                else:
                    results["stats"]["total_size_after"] += optimized["size"]
        
        # Generate SEO report
        results["stats"]["seo_report"] = analyze_seo(extracted_dir)
        
        # Create optimized zip in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(extracted_dir):
                for filename in files:
                    file_path = os.path.join(root, filename)
                    arcname = os.path.relpath(file_path, extracted_dir)
                    zipf.write(file_path, arcname)
        
        # Save zip to file for download
        optimized_zip_path = os.path.join(upload_dir, "optimized.zip")
        with open(optimized_zip_path, 'wb') as f:
            f.write(zip_buffer.getvalue())
        
        return {
            "results": results,
            "download_path": optimized_zip_path
        }
    except Exception as e:
        shutil.rmtree(upload_dir, ignore_errors=True)
        logger.error(f"Processing failed: {str(e)}")
        raise e

@app.post("/optimize/upload", response_model=OptimizationResponse)
async def optimize_upload(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    options: OptimizationRequest = None
):
    """Optimize uploaded ZIP file with options"""
    try:
        result = process_upload(file, is_github=False, options=options)
        
        # Cleanup task
        if background_tasks:
            background_tasks.add_task(
                lambda: shutil.rmtree(os.path.dirname(result["download_path"])), 
                ignore_errors=True
            )
        
        # Return the file response directly
        return FileResponse(
            result["download_path"],
            media_type="application/zip",
            headers={
                "X-Optimization-Report": json.dumps(result["results"])
            },
            filename="optimized-website.zip"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ai/analyze")
async def ai_analyze(
    request: Request,
    file: UploadFile = File(None)
):
    """
    Analyze code for performance, SEO, and accessibility using AI
    Accepts either:
    1. JSON payload with 'code' field (application/json)
    2. File upload (multipart/form-data)
    """
    try:
        content_type = request.headers.get('content-type', '')
        
        # Handle JSON payload
        if 'application/json' in content_type:
            try:
                payload = await request.json()
                logger.info(f"JSON payload: {payload}")
                
                if not payload or 'code' not in payload:
                    raise HTTPException(status_code=400, detail="JSON payload must contain 'code' field")
                
                code = payload['code']
                file_type = payload.get('file_type', 'html')  # Default to html for JSON payloads
                
                logger.info(f"Analyzing code (length: {len(code)} chars)")
                analysis = ai_optimizer.analyze_code(code, file_type)
                return {"analysis": analysis}
                
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid JSON payload")
        
        # Handle file upload
        elif file and 'multipart/form-data' in content_type:
            logger.info(f"Processing file upload: {file.filename}")
            content = await file.read()
            if len(content) > 1024 * 1024:  # 1MB limit
                raise HTTPException(status_code=400, detail="File too large")
                
            code = content.decode('utf-8')
            file_type = Path(file.filename).suffix[1:].lower()
            
            logger.info(f"Analyzing {file_type} file (size: {len(content)} bytes)")
            analysis = ai_optimizer.analyze_code(code, file_type)
            return {"analysis": analysis}
        
        raise HTTPException(
            status_code=400,
            detail="Invalid request - send either JSON with 'code' field or file upload"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ai/convert", response_model=Dict[str, str])
async def ai_convert(
    request: Request,
    file: UploadFile = File(None),
    target_format: str = Query(..., description="Target format (e.g., 'js_to_ts', 'scss_to_css')")
):
    """Convert between different code formats using AI"""
    try:
        content_type = request.headers.get('content-type', '')
        code = None
        source_format = None

        # Handle JSON payload
        if 'application/json' in content_type:
            try:
                payload = await request.json()
                logger.info("JSON payload received for conversion")
                
                # Accept either 'content' or 'code' field
                code = payload.get('content') or payload.get('code')
                if not code:
                    raise HTTPException(
                        status_code=400,
                        detail="JSON payload must contain either 'content' or 'code' field"
                    )
                
                source_format = payload.get('source_format', 'js')  # Default source format
                logger.info(f"Converting code from {source_format} to {target_format}")
                
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid JSON payload")
        
        # Handle file upload
        elif file and 'multipart/form-data' in content_type:
            logger.info(f"Processing file upload: {file.filename}")
            content = await file.read()
            if len(content) > 1024 * 1024:  # 1MB limit:
                raise HTTPException(status_code=400, detail="File too large")
                
            code = content.decode('utf-8')
            source_format = Path(file.filename).suffix[1:].lower()
            logger.info(f"Converting {source_format} to {target_format}")
        
        if not code:
            raise HTTPException(
                status_code=400,
                detail="Invalid request - send either JSON with 'content'/'code' field or file upload"
            )

        # Special case for SCSS to CSS (use libsass if available)
        if target_format == "scss_to_css" and source_format in ('scss', 'sass'):
            try:
                converted = sass.compile(string=code)
                return {"converted": converted}
            except Exception:
                logger.warning("Libsass failed, falling back to AI conversion")

        # Use AI for all conversions
        converted = ai_optimizer.convert_code(code, source_format, target_format.replace('_to_', ' '))
        return {"converted": converted}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Conversion failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ai/suggest", response_model=Dict[str, str])
async def ai_suggest(request: AIAnalysisRequest):
    """Get AI-powered optimization suggestions"""
    try:
        if not request.prompt:
            raise HTTPException(status_code=400, detail="Prompt is required")

        # Get AI suggestions
        prompt = f"""
        Provide detailed optimization suggestions for:
        {request.prompt}
        
        Include:
        1. Specific actionable recommendations
        2. Performance impact estimates
        3. Implementation difficulty
        4. Expected benefits
        5. Code examples where applicable
        
        Format as markdown with sections.
        """
        
        response = ai_optimizer.optimize_code(prompt, "suggestions")
        
        # Generate follow-up questions
        follow_up_prompt = f"""
        Based on this topic: {request.prompt}
        Generate 3 relevant follow-up questions that would help the user
        further optimize their code or website.
        Return as a JSON list.
        """
        
        follow_up_response = ai_optimizer.optimize_code(follow_up_prompt, "questions")
        try:
            follow_up_questions = json.loads(follow_up_response)
        except:
            follow_up_questions = ["How can I further improve performance?", 
                                 "What accessibility considerations should I make?", 
                                 "Are there any SEO best practices I'm missing?"]
        
        return {
            "suggestions": response,
            "follow_up_questions": follow_up_questions
        }
        
    except Exception as e:
        logger.error(f"Suggestion failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ai/seo-analyze", response_model=Dict[str, Any])
async def seo_analyze(
    url: str = Query(None, description="Website URL"),
    html_content: str = Query(None, description="Direct HTML content")
):
    """Analyze SEO for a website or HTML content using AI"""
    try:
        if url:
            # Fetch website content
            response = requests.get(url)
            content = response.text
        elif html_content:
            content = html_content
        else:
            raise HTTPException(status_code=400, detail="URL or HTML content required")

        # Get comprehensive AI SEO analysis
        seo_prompt = f"""
        Analyze this HTML content for SEO and provide:
        1. Overall SEO score (0-100)
        2. Technical SEO analysis
        3. Content quality assessment
        4. Backlink profile suggestions
        5. Mobile friendliness
        6. Page speed insights
        7. Structured data recommendations
        8. Competitor comparison if possible
        9. Actionable improvement plan
        
        Return as JSON with detailed analysis.
        
        HTML content:
        {content[:10000]}  # Limit to first 10k chars for analysis
        """
        
        analysis = ai_optimizer.analyze_code(seo_prompt, "SEO")
        
        return {
            "analysis": analysis,
            "optimized_html": ai_optimizer.optimize_code(content, "HTML") if len(content) < 5000 else "Content too large for optimization"
        }
        
    except Exception as e:
        logger.error(f"SEO analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ai/complexity", response_model=Dict[str, Any])
async def code_complexity(
    request: AIAnalysisRequest
):
    """Analyze code complexity using AI"""
    try:
        if not request.code:
            raise HTTPException(status_code=400, detail="Code is required")
        
        prompt = f"""
        Analyze this {request.file_type or 'code'} for complexity and provide:
        1. Cyclomatic complexity score
        2. Cognitive complexity score
        3. Maintainability index
        4. Potential refactoring opportunities
        5. Code smell detection
        6. Performance bottlenecks
        
        Return as JSON with detailed metrics.
        
        Code:
        {request.code}
        """
        
        analysis = ai_optimizer.analyze_code(prompt, "complexity")
        return {"complexity_analysis": analysis}
        
    except Exception as e:
        logger.error(f"Complexity analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ai/accessibility", response_model=Dict[str, Any])
async def accessibility_check(
    request: AIAnalysisRequest
):
    """Check code for accessibility issues using AI"""
    try:
        if not request.code and not request.prompt:
            raise HTTPException(status_code=400, detail="Code or prompt is required")
        
        content = request.code if request.code else request.prompt
        file_type = request.file_type if request.file_type else ("html" if not request.code else "code")
        
        prompt = f"""
        Analyze this {file_type} content for accessibility issues and provide:
        1. WCAG compliance level (A/AA/AAA)
        2. Specific accessibility violations
        3. Screen reader compatibility
        4. Color contrast issues
        5. Keyboard navigation problems
        6. ARIA implementation suggestions
        7. Mobile accessibility
        
        Return as JSON with detailed findings.
        
        Content:
        {content}
        """
        
        analysis = ai_optimizer.analyze_code(prompt, "accessibility")
        return {"accessibility_analysis": analysis}
        
    except Exception as e:
        logger.error(f"Accessibility check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ai/react-convert", response_model=Dict[str, str])
async def react_conversion(
    request: AIAnalysisRequest
):
    """Convert code to React components using AI"""
    try:
        if not request.code:
            raise HTTPException(status_code=400, detail="Code is required")
        
        prompt = f"""
        Convert this {request.file_type or 'code'} to a modern React component with:
        1. Functional component style
        2. TypeScript typing
        3. React hooks
        4. Proper prop handling
        5. Clean, modular code
        6. Comments for key parts
        
        Return ONLY the converted code, no explanations.
        
        Original code:
        {request.code}
        """
        
        converted = ai_optimizer.optimize_code(prompt, "react")
        return {"converted": converted}
        
    except Exception as e:
        logger.error(f"React conversion failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def download_github_repo(repo_url: str, dest_dir: str) -> str:
    """Download GitHub repository as zip"""
    try:
        # Extract owner/repo from URL
        match = re.match(r'https://github\.com/([^/]+)/([^/]+)', repo_url)
        if not match:
            raise ValueError("Invalid GitHub URL format")
        
        owner, repo = match.groups()
        if repo.endswith('.git'):
            repo = repo[:-4]
        
        # Download zip
        zip_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/main.zip"
        response = requests.get(zip_url)
        response.raise_for_status()
        
        # Save zip file
        zip_path = os.path.join(dest_dir, f"{repo}.zip")
        with open(zip_path, 'wb') as f:
            f.write(response.content)
        
        return zip_path
    except Exception as e:
        logger.error(f"GitHub download failed: {str(e)}")
        raise HTTPException(status_code=400, detail=f"GitHub download failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)