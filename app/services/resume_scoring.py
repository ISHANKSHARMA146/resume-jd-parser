from app.utils.file_parser import parse_pdf_or_docx
from app.services.gpt_service import GPTService
from app.services.config_service import ConfigService
from io import BytesIO
from app.utils.logger import Logger
from app.models.schemas import ResumeSchema, JobDescriptionEnhancementResponse, ResumeScoringSchema
from datetime import datetime
from typing import List, Dict

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

    async def process_bulk_resumes(self, resume_files: List[BytesIO], filenames: List[str]) -> List[Dict[str, any]]:
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

    async def parse_resume(self, file_buffer: BytesIO, filename: str) -> Dict[str, any]:
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

            Key instructions for duration calculations:
            - Calculate work_experience and educations_duration based on the start and end dates. Ensure that consecutive periods (without gaps) are treated as distinct and add up the durations without including the gap between roles.
            - If "present," "ongoing," or similar terms like these are mentioned, then use today's date {today_date} as the date_end and calculate the duration accordingly.
            """

            user_prompt = f"""
            Extract structured information from this resume text:
            {text}
            Follow these instructions:
            1. Parse the text and extract structured information according to the keys mentioned above.
            2. Ensure that the total work experience is calculated accurately by accounting for overlaps and distinct periods.
            3. Handle ongoing periods by comparing "present" with today's date and calculating the accurate duration.
            4. For overlapping roles, calculate the total unique time worked without double-counting.
            5. For education durations, calculate accurately.
            6. Ensure no missing fields, and if any information is not provided, use null or empty arrays.
            7. Return a valid JSON output with accurate dates and durations.
            8. If no skills are explicitly or less than 10 are mentioned in the resume, generate a total of 10 relevant skills based on the candidate's experience and education.
            """

            structured_data = await self.gpt_service.extract_with_prompts(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                response_schema=ResumeSchema
            )

            if structured_data.get('experiences'):
                experiences_array = structured_data['experiences']
                if not isinstance(experiences_array, list):
                    experiences_array = [experiences_array]

                structured_data['work_experience'] = self.calculate_total_work_experience(
                    [{'date_start': exp['date_start'], 'date_end': exp['date_end']} for exp in experiences_array]
                )

            return structured_data

        except Exception as e:
            logger.error(f"Error extracting resume details: {str(e)}", exc_info=True)
            raise

    async def compare_resume_with_jd_and_candidates(self, resume: Dict[str, any], enhanced_jd: Dict[str, any], candidates: List[Dict[str, any]]) -> Dict[str, any]:
        """
        Compares an extracted resume against the enhanced job description and sample candidates.

        Args:
            resume (Dict[str, any]): Extracted resume details.
            enhanced_jd (Dict[str, any]): The enhanced job description.
            candidates (List[Dict[str, any]]): List of six generated candidate profiles.

        Returns:
            Dict with resume score, closest matching candidate, and improvement recommendations.
        """
        try:
            system_prompt = f"""
            You are an AI evaluating resumes against an enhanced job description and sample candidates.
            Your task is to analyze how well a candidate's resume aligns with both.

            **Scoring Criteria:**
            1 **Skill Match** (Technical & Soft Skills).
            2 **Experience Relevance** (Past roles, industry).
            3 **Education & Certifications** (Matching Degree & Certifications).
            4 **Keyword Similarity** (ATS optimization).
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
            return datetime.now()  # If the date is invalid, return the current date
