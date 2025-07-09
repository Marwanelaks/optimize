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
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1"
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
                model="google/gemini-2.0-flash-001",
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
        2. SEO score (0-100)
        3. Accessibility score (0-100)
        4. 3 specific optimization suggestions
        5. Estimated optimization potential (0-100%)
        
        Return as JSON with these keys:
        - performance_score
        - seo_score
        - accessibility_score
        - suggestions
        - optimization_potential
        """
        
        try:
            response = self.client.chat.completions.create(
                model="google/gemini-2.0-flash-001",
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
                "optimization_potential": 0
            }

ai_optimizer = AIOptimizer()

def optimize_image(image_path: str, aggressive: bool = False) -> str:
    """Optimize image and convert to WebP format"""
    try:
        with Image.open(image_path) as img:
            # Convert to WebP
            webp_path = f"{os.path.splitext(image_path)[0]}.webp"
            quality = 75 if aggressive else 85
            
            # Preserve transparency for PNGs
            if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                img.save(webp_path, 'WEBP', quality=quality, lossless=False, method=6)
            else:
                img.save(webp_path, 'WEBP', quality=quality, method=6)
            
            # Remove original image
            os.remove(image_path)
            return webp_path
    except Exception as e:
        logger.error(f"Error optimizing image {image_path}: {str(e)}")
        return image_path

# Add these functions ABOVE the process_upload() function in your code:

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
    """Optimize image and convert to WebP format"""
    try:
        with Image.open(image_path) as img:
            # Convert to WebP
            webp_path = f"{os.path.splitext(image_path)[0]}.webp"
            quality = 75 if aggressive else 85
            
            # Preserve transparency for PNGs
            if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                img.save(webp_path, 'WEBP', quality=quality, lossless=False, method=6)
            else:
                img.save(webp_path, 'WEBP', quality=quality, method=6)
            
            # Remove original image
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
    """Analyze and improve SEO for all HTML files"""
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
                    
                    # Apply basic SEO improvements
                    soup = BeautifulSoup(content, 'html.parser')
                    head = soup.find('head')
                    if head:
                        if not soup.find('meta', attrs={'name': 'description'}):
                            meta = soup.new_tag('meta', attrs={
                                'name': 'description',
                                'content': 'Optimized website with AI assistance'
                            })
                            head.append(meta)
                        
                        if not soup.find('meta', attrs={'charset': True}):
                            meta = soup.new_tag('meta', attrs={'charset': 'UTF-8'})
                            head.insert(0, meta)
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(str(soup))
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


# Add these endpoints to your existing FastAPI app

@app.post("/ai/analyze")
async def ai_analyze(
    request: Request,
    file: UploadFile = File(None)
):
    """
    Analyze code for performance, SEO, and accessibility
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
                file_type = 'html'  # Default for JSON payloads
                
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
    target_format: str = Query(..., description="Target format (e.g., 'scss_to_css')")
):
    """Convert between different code formats"""
    try:
        content_type = request.headers.get('content-type', '')
        code = None
        file_type = None

        # Handle JSON payload
        if 'application/json' in content_type:
            try:
                payload = await request.json()
                logger.info(f"JSON payload received for conversion")
                
                # Accept either 'content' or 'code' field
                if not payload:
                    raise HTTPException(status_code=400, detail="Empty JSON payload")
                
                code = payload.get('content') or payload.get('code')
                if not code:
                    raise HTTPException(
                        status_code=400,
                        detail="JSON payload must contain either 'content' or 'code' field"
                    )
                
                logger.info(f"Converting code (length: {len(code)} chars)")
                
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
            logger.info(f"Converting {file_type} file (size: {len(content)} bytes)")
        
        if not code:
            raise HTTPException(
                status_code=400,
                detail="Invalid request - send either JSON with 'content'/'code' field or file upload"
            )

        # Rest of your conversion logic remains the same
        if target_format == "scss_to_css":
            converted = sass.compile(string=code)
        elif target_format == "css_to_scss":
            converted = convert_css_to_scss(code)
        elif target_format == "js_to_ts":
            converted = ai_optimizer.optimize_code(
                f"Convert this JavaScript code to TypeScript:\n\n{code}",
                "TypeScript conversion"
            )
        elif target_format == "html_to_jsx":
            converted = convert_html_to_jsx(code)
        else:
            raise HTTPException(status_code=400, detail="Unsupported conversion type")

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

        response = ai_optimizer.optimize_code(request.prompt, "suggestion")
        
        # Format the response as markdown with bullet points
        formatted_response = format_as_markdown(response)
        
        return {
            "response": formatted_response,
            "follow_up_questions": generate_follow_up_questions(request.prompt)
        }
        
    except Exception as e:
        logger.error(f"Suggestion failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ai/seo-analyze", response_model=Dict[str, Any])
async def seo_analyze(
    url: str = Query(None, description="Website URL"),
    html_content: str = Query(None, description="Direct HTML content")
):
    """Analyze SEO for a website or HTML content"""
    try:
        if url:
            # Fetch website content
            response = requests.get(url)
            content = response.text
        elif html_content:
            content = html_content
        else:
            raise HTTPException(status_code=400, detail="URL or HTML content required")

        # Basic SEO analysis
        soup = BeautifulSoup(content, 'html.parser')
        
        # Get AI analysis
        analysis = ai_optimizer.analyze_code(content, "HTML")
        
        # Additional SEO checks
        seo_report = {
            "analysis": analysis,
            "checks": {
                "title": check_seo_title(soup),
                "meta_description": check_meta_description(soup),
                "headings": check_headings_structure(soup),
                "images": check_image_alt_tags(soup),
                "links": check_internal_links(soup),
                "mobile_friendly": check_mobile_friendliness(content)
            }
        }
        
        return seo_report
        
    except Exception as e:
        logger.error(f"SEO analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Helper functions for the APIs

def calculate_code_complexity(code: str, file_type: str) -> Dict[str, Any]:
    """Calculate code complexity metrics"""
    # Implement complexity analysis based on file type
    return {
        "cyclomatic_complexity": estimate_cyclomatic_complexity(code, file_type),
        "maintainability_index": calculate_maintainability_index(code, file_type)
    }

def suggest_performance_improvements(code: str, file_type: str) -> List[str]:
    """Generate performance improvement suggestions"""
    prompt = f"Suggest 3 specific performance improvements for this {file_type} code:\n\n{code}"
    response = ai_optimizer.optimize_code(prompt, "suggestions")
    return [s.strip() for s in response.split('\n') if s.strip()]

def suggest_seo_improvements(code: str, file_type: str) -> List[str]:
    """Generate SEO improvement suggestions for HTML"""
    if file_type not in ('html', 'htm'):
        return ["SEO suggestions only available for HTML content"]
    
    prompt = f"Suggest 3 specific SEO improvements for this HTML:\n\n{code}"
    response = ai_optimizer.optimize_code(prompt, "suggestions")
    return [s.strip() for s in response.split('\n') if s.strip()]

def suggest_accessibility_improvements(code: str, file_type: str) -> List[str]:
    """Generate accessibility improvement suggestions"""
    prompt = f"Suggest 3 specific accessibility improvements for this {file_type} code:\n\n{code}"
    response = ai_optimizer.optimize_code(prompt, "suggestions")
    return [s.strip() for s in response.split('\n') if s.strip()]

def convert_css_to_scss(css: str) -> str:
    """Convert CSS to SCSS format"""
    # Basic conversion - AI could do better
    return css.replace('}', '}\n\n')

def convert_html_to_jsx(html: str) -> str:
    """Convert HTML to JSX format"""
    prompt = f"Convert this HTML to JSX:\n\n{html}"
    return ai_optimizer.optimize_code(prompt, "JSX conversion")

def format_as_markdown(text: str) -> str:
    """Format plain text as markdown with bullet points"""
    lines = [f"- {line.strip()}" for line in text.split('\n') if line.strip()]
    return '\n'.join(lines)

def generate_follow_up_questions(prompt: str) -> List[str]:
    """Generate relevant follow-up questions"""
    prompt = f"Generate 3 relevant follow-up questions about: {prompt}"
    response = ai_optimizer.optimize_code(prompt, "questions")
    return [q.strip() for q in response.split('\n') if q.strip()]

# SEO Check helper functions

def check_seo_title(soup: BeautifulSoup) -> Dict[str, Any]:
    """Check SEO title tag"""
    title = soup.find('title')
    return {
        "exists": title is not None,
        "value": title.string if title else None,
        "length": len(title.string) if title else 0,
        "optimal_length": "50-60 characters"
    }

def check_meta_description(soup: BeautifulSoup) -> Dict[str, Any]:
    """Check meta description"""
    meta = soup.find('meta', attrs={'name': 'description'})
    return {
        "exists": meta is not None,
        "value": meta['content'] if meta else None,
        "length": len(meta['content']) if meta else 0,
        "optimal_length": "150-160 characters"
    }

def check_headings_structure(soup: BeautifulSoup) -> Dict[str, Any]:
    """Check heading hierarchy"""
    headings = {f'h{i}': len(soup.find_all(f'h{i}')) for i in range(1, 7)}
    return {
        "count": headings,
        "recommendation": "Should have proper hierarchy (one h1, then h2, etc.)"
    }

def check_image_alt_tags(soup: BeautifulSoup) -> Dict[str, Any]:
    """Check image alt attributes"""
    images = soup.find_all('img')
    missing_alt = sum(1 for img in images if not img.get('alt'))
    return {
        "total_images": len(images),
        "missing_alt": missing_alt,
        "percentage_with_alt": f"{((len(images)-missing_alt)/len(images)*100):.1f}%" if images else "N/A"
    }

def check_internal_links(soup: BeautifulSoup) -> Dict[str, Any]:
    """Check internal linking structure"""
    links = soup.find_all('a')
    return {
        "total_links": len(links),
        "internal_links": sum(1 for link in links if link.get('href', '').startswith('/')),
        "external_links": sum(1 for link in links if link.get('href', '').startswith('http'))
    }

def check_mobile_friendliness(html: str) -> Dict[str, Any]:
    """Basic mobile friendliness check"""
    viewport = 'viewport' in html.lower()
    return {
        "viewport_meta": viewport,
        "recommendation": "Include <meta name='viewport'> tag for mobile"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)