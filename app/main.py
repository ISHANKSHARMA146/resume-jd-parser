from fastapi import FastAPI, HTTPException, File, UploadFile
from io import BytesIO
from app.services.resume_extraction import ResumeParser
from app.services.jd_extraction_helper import JobDescriptionParser
from app.utils.logger import Logger

# Initialize Logger
logger = Logger(__name__).get_logger()

# Initialize FastAPI App
app = FastAPI(
    title="Resume and Job Description Parser API",
    description="API for extracting structured data from resumes and job descriptions",
    version="1.0.0"
)

# Initialize Services
resume_parser = ResumeParser()
jd_parser = JobDescriptionParser()

@app.get("/")
async def root():
    return {"message": "Resume and JD Parser API is running!"}

@app.post("/api/parse-resume/")
async def parse_resume(file: UploadFile = File(...)):
    """
    Endpoint to parse a resume file (PDF or DOCX) and return structured JSON output.
    """
    try:
        file_buffer = BytesIO(await file.read())  
        filename = file.filename

        result = await resume_parser.parse_resume(file_buffer, filename)
        return result
    except Exception as e:
        logger.error(f"Error parsing resume file '{file.filename}': {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error parsing resume: {str(e)}")

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

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Resume and JD Parser API")
    uvicorn.run(app, host="0.0.0.0", port=8000)
