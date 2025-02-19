from app.utils.file_parser import parse_pdf_or_docx
from app.services.gpt_service import GPTService
from app.services.config_service import ConfigService
from io import BytesIO
from app.utils.logger import Logger
from app.models.schemas import EnhancedJobDescriptionSchema, CandidateProfileSchemaList
from datetime import datetime
from typing import List, Dict, Any

logger = Logger(__name__).get_logger()

class JobDescriptionEnhancer:
    """
    Service for extracting and enhancing job descriptions, followed by generating sample candidate profiles.
    """

    def __init__(self):
        """
        Initializes the Job Description Enhancer with GPT integration.
        """
        logger.info("JobDescriptionEnhancer initialized successfully.")
        config = ConfigService()
        self.gpt_service = GPTService()
        self.temp_storage = {}  # Temporary storage for enhanced JD and generated candidates

    async def enhance_job_description(self, file_buffer: BytesIO, filename: str):
        """
        Extracts, enhances a job description, and generates sample candidate profiles.

        Args:
            file_buffer (BytesIO): The job description file buffer.
            filename (str): Name of the uploaded job description file.

        Returns:
            Dict containing the enhanced job description and generated candidates.
        """
        try:
            # Extract the job description
            extracted_jd = await self.extract_job_description(file_buffer, filename)

            # Enhance the job description
            enhanced_jd = await self.generate_enhanced_jd(extracted_jd)

            # Store Enhanced JD
            self.temp_storage["enhanced_job_description"] = enhanced_jd

            # Generate 6 Sample Candidates based on enhanced JD
            candidates = await self.generate_candidate_profiles(enhanced_jd)

            # Store Generated Candidates
            self.temp_storage["candidates"] = candidates

            return {
                "enhanced_job_description": enhanced_jd,
                "generated_candidates": candidates
            }

        except Exception as e:
            logger.error(f"Error enhancing job description '{filename}': {str(e)}", exc_info=True)
            raise

    async def extract_job_description(self, file_buffer: BytesIO, filename: str) -> Dict[str, Any]:
        """
        Extracts raw text from a job description file.

        Args:
            file_buffer (BytesIO): The job description file buffer.
            filename (str): Name of the uploaded job description file.

        Returns:
            Dict containing extracted job description details.
        """
        try:
            # Extract text from the file
            text = parse_pdf_or_docx(file_buffer, filename)

            system_prompt = f"""
            You are an AI model specializing in extracting structured job descriptions.
            Extract relevant details from the provided job description text and return them in the following JSON format:

            {{
                "job_title": "string",
                "role_summary": "string",
                "responsibilities": ["string", "string"],
                "required_skills": ["string", "string"],
                "experience_level": "string",
                "key_metrics": ["string", "string"]
            }}
            """

            user_prompt = f"""
            Extract key details from this job description:

            {text}
            """

            # Extract structured data from GPT
            extracted_jd = await self.gpt_service.extract_with_prompts(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                response_schema=EnhancedJobDescriptionSchema
            )

            return extracted_jd

        except Exception as e:
            logger.error(f"Error extracting job description '{filename}': {str(e)}", exc_info=True)
            raise

    async def generate_enhanced_jd(self, extracted_jd: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhances the extracted job description.

        Args:
            extracted_jd (Dict[str, Any]): Extracted job description details.

        Returns:
            Dict containing the enhanced job description.
        """
        try:
            system_prompt = f"""
            You are an AI expert at refining and enhancing job descriptions. Your task is to take the extracted job description provided and enhance it by improving its clarity, structure, and detail. The goal is to produce a well-structured and highly detailed job description that can be easily understood by job seekers and is aligned with industry standards.

            The enhanced job description should follow this JSON format:

            {{
                "job_title": "string",
                "role_summary": "string",
                "responsibilities": ["string", "string", ...],
                "required_skills": ["string", "string", ...],
                "experience_level": "string",
                "key_metrics": ["string", "string", ...],
                "working_conditions": "string",
                "growth_opportunities": "string",
                "company_culture": "string"
            }}
            """

            user_prompt = f"""
            Improve the following job description to be more structured and detailed:
            - responsibilities to have minimum 10 generated
            - required_skills to have minimum 15 generated
            - key_metrics to be minimum 10 generated

            {extracted_jd}
            """

            # Generate the enhanced job description
            enhanced_jd = await self.gpt_service.extract_with_prompts(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                response_schema=EnhancedJobDescriptionSchema
            )

            return enhanced_jd

        except Exception as e:
            logger.error(f"Error generating enhanced job description: {str(e)}", exc_info=True)
            raise

    async def generate_candidate_profiles(self, enhanced_jd: Dict[str, Any]) -> CandidateProfileSchemaList:
        """
        Generates six candidate profiles based on the enhanced job description.

        Args:
            enhanced_jd (Dict[str, Any]): The enhanced job description.

        Returns:
            CandidateProfileSchemaList: List of six sample candidate profiles.
        """
        try:
            system_prompt = f"""
            You are an AI that creates sample candidate profiles for job matching.
            Based on the given job description, generate six sample candidates, each with varying levels of qualification:

            - 10/10: Ideal candidate (perfect fit)
            - 8/10: Strong candidate (minor gaps)
            - 6/10: Good but not the best fit
            - 4/10: Below average
            - 2/10: Weak fit
            - 0/10: Not a fit

            Each candidate profile should follow this JSON format:

            {{
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
            }}
            """

            user_prompt = f"""
            Generate six sample candidates with varying levels of fit for this job description:
            1. Parse the text and extract structured information according to the keys mentioned above.
            2. Ensure that the total work experience is calculated accurately by accounting for overlaps and distinct periods.
            3. Handle ongoing periods by comparing "present" with today's date and calculating the accurate duration.
            4. For overlapping roles, calculate the total unique time worked without double-counting.
            5. For education durations, calculate accurately.
            6. Ensure no missing fields, and if any information is not provided, use null or empty arrays.
            7. Return a valid JSON output with accurate dates and durations.

            {enhanced_jd}
            """

            # Generate the list of candidates
            candidates = await self.gpt_service.extract_with_prompts(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                response_schema=CandidateProfileSchemaList
            )

            return candidates

        except Exception as e:
            logger.error(f"Error generating candidate profiles: {str(e)}", exc_info=True)
            raise
