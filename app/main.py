from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Body
from io import BytesIO
from typing import List
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from app.services.resume_extraction import ResumeParser
from app.services.jd_extraction_helper import JobDescriptionParser
from app.services.job_description_enhance import JobDescriptionEnhancer
from app.services.resume_scoring import ResumeScoringService
from app.services.resume_generation import ResumeGenerationService
from app.utils.logger import Logger

# Initialize Logger
logger = Logger(__name__).get_logger()

# Initialize FastAPI App
app = FastAPI(
    title="Resume and Job Description Processing API",
    description="API for extracting, enhancing, and scoring resumes and job descriptions",
    version="1.0.0"
)

# CORS Configuration - Allow requests from React frontend running on localhost:3000
origins = [
    "http://localhost:8000"
]

# Serve static files (HTML UI)
app.mount("/static", StaticFiles(directory="app"), name="static")

@app.get("/")
async def serve_ui():
    return FileResponse(os.path.join("app", "index.html"))

# Initialize Services
resume_parser = ResumeParser()
jd_parser = JobDescriptionParser()
job_description_enhancer = JobDescriptionEnhancer()
resume_scoring_service = ResumeScoringService(job_description_enhancer)
resume_generation_service = ResumeGenerationService()

@app.get("/")
async def root():
    return {"message": "Resume and JD Processing API is running!"}

### **Resume Parsing Endpoint**
@app.post("/api/parse-resume/")
async def parse_resume(file: UploadFile = File(...)):
    """
    Endpoint to parse a resume file (PDF, DOCX, DOC, image) and return structured JSON output.
    """
    try:
        file_buffer = BytesIO(await file.read())  
        filename = file.filename
        result = await resume_parser.parse_resume(file_buffer, filename)
        return result
    except Exception as e:
        logger.error(f"Error parsing resume file '{file.filename}': {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error parsing resume: {str(e)}")

### **Job Description Parsing Endpoint**
@app.post("/api/parse-job-description/")
async def parse_job_description(file: UploadFile = File(...)):
    """
    Endpoint to parse a job description file (PDF or DOCX) and return structured JSON output.
    """
    try:
        file_buffer = BytesIO(await file.read())
        filename = file.filename
        result = await jd_parser.parse_job_description(file_buffer, filename)
        return result
    except Exception as e:
        logger.error(f"Error parsing job description file '{file.filename}': {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error parsing job description: {str(e)}")

### **Job Description Enhancement Endpoint**
@app.post("/api/job-description-enhance/")
async def job_description_enhance(file: UploadFile = File(...)):
    """
    Endpoint to enhance a job description by extracting and structuring details, 
    improving clarity, and generating sample candidate profiles.
    """
    try:
        file_buffer = BytesIO(await file.read())
        filename = file.filename
        result = await job_description_enhancer.enhance_job_description(file_buffer, filename)
        return result
    except Exception as e:
        logger.error(f"Error enhancing job description '{file.filename}': {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error enhancing job description: {str(e)}")

### **Resume Scoring Endpoint**
@app.post("/api/score-resumes/")
async def score_resumes(
    files: List[UploadFile] = File(...),
    user_input: str = Form("")  # Capture additional user input from frontend
):
    """
    Endpoint to score multiple resumes against an enhanced job description and sample candidate profiles,
    while incorporating additional user preferences.
    """
    try:
        if not files:
            raise HTTPException(status_code=400, detail="No resume files provided.")

        resume_files = [BytesIO(await file.read()) for file in files]
        filenames = [file.filename for file in files]
        result = await resume_scoring_service.process_bulk_resumes(resume_files, filenames, user_input)
        return result
    except Exception as e:
        logger.error(f"Error scoring resumes: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error scoring resumes: {str(e)}")

### **Resume Generation from Uploaded Resume Endpoint**
@app.post("/api/generate-resume-from-upload/")
async def generate_resume_from_upload(file: UploadFile = File(...), download_format: str = Form("html")):
    """
    Endpoint to generate an ATS optimized resume from an uploaded resume file.
    It extracts resume details, enhances them for ATS optimization,
    and returns a well-formatted resume in the requested format (html, pdf, or docx).
    """
    try:
        file_buffer = BytesIO(await file.read())
        filename = file.filename
        generated_resume_content = await resume_generation_service.generate_resume_from_upload(file_buffer, filename, output_format=download_format)
        output_filename = f"generated_resume.{download_format}"
        with open(output_filename, "wb") as f:
            f.write(generated_resume_content)
        if download_format.lower() == "pdf":
            media_type = "application/pdf"
        elif download_format.lower() == "docx":
            media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        else:
            media_type = "text/html"
        return FileResponse(output_filename, media_type=media_type, filename=output_filename)
    except Exception as e:
        logger.error(f"Error generating resume from upload '{file.filename}': {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating resume: {str(e)}")

### **Resume Generation from Manual Form Endpoint**
@app.post("/api/generate-resume-from-form/")
async def generate_resume_from_form(candidate_data: dict = Body(...), download_format: str = Form("html")):
    """
    Endpoint to generate an ATS optimized resume from manually provided candidate data.
    Candidate data is provided as JSON.
    """
    try:
        generated_resume_content = await resume_generation_service.generate_resume_from_form(candidate_data, output_format=download_format)
        output_filename = f"generated_resume.{download_format}"
        with open(output_filename, "wb") as f:
            f.write(generated_resume_content)
        if download_format.lower() == "pdf":
            media_type = "application/pdf"
        elif download_format.lower() == "docx":
            media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        else:
            media_type = "text/html"
        return FileResponse(output_filename, media_type=media_type, filename=output_filename)
    except Exception as e:
        logger.error(f"Error generating resume from form data: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating resume: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Resume and JD Processing API")
    uvicorn.run(app, host="0.0.0.0", port=8000)