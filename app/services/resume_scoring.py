from app.utils.file_parser import parse_pdf_or_docx
from app.services.gpt_service import GPTService
from app.services.config_service import ConfigService
from io import BytesIO
from app.utils.logger import Logger
from app.models.schemas import ResumeSchema, ResumeScoringSchema, ResumeScoringResponse
from datetime import datetime
from typing import List, Dict, Any

logger = Logger(__name__).get_logger()

class ResumeScoringService:
    """
    Service for extracting structured resume details, scoring resumes against the enhanced job description 
    and sample candidates, and returning a structured comparison report.
    """

    def __init__(self, job_description_enhancer):
        """
        Initializes the Resume Scoring Service with GPT integration.
        """
        logger.info("ResumeScoringService initialized successfully.")
        config = ConfigService()
        self.gpt_service = GPTService()
        self.job_description_enhancer = job_description_enhancer  # Reference to Enhanced JD & Candidates

    async def process_bulk_resumes(self, resume_files: List[BytesIO], filenames: List[str]) -> List[Dict[str, Any]]:
        """
        Processes multiple resumes, extracts structured data, and compares them to the enhanced job description 
        and sample candidates.

        Args:
            resume_files (List[BytesIO]): List of resume file buffers.
            filenames (List[str]): Corresponding filenames.

        Returns:
            List of structured resume analysis results with scores and comparisons.
        """
        try:
            if "enhanced_job_description" not in self.job_description_enhancer.temp_storage:
                raise ValueError("Enhanced Job Description not found. Run /api/job-description-enhance first.")

            enhanced_jd = self.job_description_enhancer.temp_storage["enhanced_job_description"]
            generated_candidates = self.job_description_enhancer.temp_storage["candidates"]

            results = []
            for file_buffer, filename in zip(resume_files, filenames):
                logger.info(f"Processing resume file: {filename}")

                # **Extract Resume Data**
                extracted_resume = await self.parse_resume(file_buffer, filename)

                # **Compare Resume Against JD & Sample Candidates**
                resume_comparison = await self.compare_resume_with_jd_and_candidates(extracted_resume, enhanced_jd, generated_candidates)

                # **Store Results**
                results.append(resume_comparison)

            return results

        except Exception as e:
            logger.error(f"Error processing resumes: {str(e)}", exc_info=True)
            raise

    async def parse_resume(self, file_buffer: BytesIO, filename: str) -> Dict[str, Any]:
        """
        Parses a resume file and extracts structured information.

        Args:
            file_buffer (BytesIO): The resume file buffer.
            filename (str): Name of the uploaded resume file.

        Returns:
            Dict containing structured resume data.
        """
        try:
            text = parse_pdf_or_docx(file_buffer, filename)
            today_date = datetime.now().strftime("%Y-%m-%d")

            system_prompt = f"""
            You are an AI model specializing in extracting structured information from resumes.
            Parse the text and produce a JSON structure with these top-level fields, each of the following keys must be present:
            1) candidate_name (string) — Full name, ensure spaces between first and last names if applicable.
            2) email_address (string) - The email should be a valid email address with a "@" symbol and a domain name (gmail, outlook, etc..).
            3) phone_number (string) - should be a valid phone number with country codes (default is +91 if none given) first, followed by a space and then the number.
            4) work_experience (object containing 'years' (number) and 'months' (number)) - Ensure that overlapping work periods are handled correctly.
            5) educations_duration (object containing 'years' (number) and 'months' (number)) — Calculate the correct total duration for education.
            6) experiences (array of objects):
                Each experience must include:
                - key (string),
                - title (string),
                - description (string),
                - date_start (string),
                - date_end (string),
                - skills (array of strings),
                - certifications (array of strings),
                - courses (array of strings),
                - tasks (array of strings),
                - languages (array of strings),
                - interests (array of strings),
                - company (string)
            7) educations (array of objects, similar to experiences):
                - key (string),
                - title (string),
                - description (string),
                - date_start (string),
                - date_end (string),
                - school (string)
            8) social_urls (array of objects, each with:
                - type (string),
                - url (string)
            9) languages (array of objects, each with:
                - name (string)
            10) skills (object containing 'primary_skills' (array of strings) and 'secondary_skills' (array of strings))
            """

            user_prompt = f"""
            Extract structured information from this resume text:
            {text}
            """

            extracted_resume = await self.gpt_service.extract_with_prompts(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                response_schema=ResumeSchema
            )

            if extracted_resume.get('experiences'):
                experiences_array = extracted_resume['experiences']
                if not isinstance(experiences_array, list):
                    experiences_array = [experiences_array]

                extracted_resume['work_experience'] = self.calculate_total_work_experience(
                    [{'date_start': exp['date_start'], 'date_end': exp['date_end']} for exp in experiences_array]
                )

            return extracted_resume

        except Exception as e:
            logger.error(f"Error extracting resume details: {str(e)}", exc_info=True)
            raise

    async def compare_resume_with_jd_and_candidates(self, resume: Dict[str, Any], enhanced_jd: Dict[str, Any], candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compares an extracted resume against the enhanced job description and sample candidates.

        Args:
            resume (Dict[str, Any]): Extracted resume details.
            enhanced_jd (Dict[str, Any]): The enhanced job description.
            candidates (List[Dict[str, Any]]): List of six generated candidate profiles.

        Returns:
            Dict with resume score, closest matching candidate, and improvement recommendations.
        """
        try:
            system_prompt = f"""
            You are an AI evaluating resumes against an enhanced job description and sample candidates.
            Your task is to analyze how well a candidate's resume aligns with both.

            **Scoring Criteria:**
            1. **Skill Match** (Technical & Soft Skills).
            2. **Experience Relevance** (Past roles, industry).
            3. **Education & Certifications** (Matching Degree & Certifications).
            4. **Keyword Similarity** (ATS optimization).

            Provide a structured JSON response strictly following the schema.
            """

            user_prompt = f"""
            Evaluate the following resume against the **Enhanced Job Description** and **Sample Candidates**.

            **Enhanced Job Description:**
            {enhanced_jd}

            **Candidate Resume:**
            {resume}

            **Sample Candidates:**
            {candidates}
            """

            resume_comparison = await self.gpt_service.extract_with_prompts(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                response_schema=ResumeScoringSchema
            )

            return resume_comparison

        except Exception as e:
            logger.error(f"Error comparing resume: {str(e)}", exc_info=True)
            raise

    def calculate_total_work_experience(self, experiences: List[Dict[str, str]]) -> Dict[str, int]:
        if not experiences:
            return {'years': 0, 'months': 0}
        total_months = sum((self.parse_date(exp['date_end']).year - self.parse_date(exp['date_start']).year) * 12 + (self.parse_date(exp['date_end']).month - self.parse_date(exp['date_start']).month) for exp in experiences)
        return {'years': total_months // 12, 'months': total_months % 12}

    def parse_date(self, date_string: str) -> datetime:
        try:
            return datetime.strptime(date_string, '%Y-%m-%d')
        except ValueError:
            return datetime.now()
