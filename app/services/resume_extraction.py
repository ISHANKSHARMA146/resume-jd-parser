from app.utils.file_parser import parse_pdf_or_docx
from app.services.gpt_service import GPTService
from app.services.config_service import ConfigService
from io import BytesIO
from app.utils.logger import Logger
from app.models.schemas import ResumeSchema
from datetime import datetime

logger = Logger(__name__).get_logger()

class ResumeParser:
    """
    Service for extracting structured information from resumes.
    """
    def __init__(self):
        """
        Initializes the Resume Parser with GPT integration.
        """
        logger.info("ResumeParser initialized successfully.")
        config = ConfigService()
        self.gpt_service = GPTService()

    async def parse_resume(self, file_buffer: BytesIO, filename: str):
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

            # System Prompt
            system_prompt = f"""
            You are an AI specialized in extracting structured information from resumes. 
            Ensure accurate duration calculations and provide structured JSON output. 
            Today's date is {today_date}. Follow these rules:

            1. **Extract Fields**:
               - candidate_name
               - email_address
               - phone_number
               - skills (avoid duplicates)
               - languages (explicitly mentioned ones)

            2. **Education**:
               - degree
               - institution
               - duration: 
                 a. If start and end years are given, calculate total years/months.
                 b. If only one year is given, infer duration based on past education or standard durations.
                 c. If explicit duration is mentioned, use it.
                 d. Validate against institution norms for consistency.
               - cgpa (if available)

            3. **Total Education Duration**:
               - Sum up the durations and ensure consistency, considering overlapping periods.

            4. **Work Experience**:
               - company
               - role
               - duration:
                 a. If start and end dates are provided, calculate exact duration.
                 b. If only a start date exists, calculate up to {today_date}.
                 c. If explicit duration is mentioned, use it.
                 d. Validate against industry norms to infer missing values.
               - description
               - location
               - skills used
               - tasks performed

            5. **Total Work Experience**:
               - Sum all work durations, handling overlaps properly.

            6. **Social URLs**:
               - Extract LinkedIn, GitHub, or any professional links.

            Additional Guidelines:
            - Avoid using 'unknown', 'ongoing', or vague terms.
            - Ensure numeric outputs for durations.
            - Use contextual knowledge for missing or unclear details.
            """

            # User Prompt
            user_prompt = f"""
            Extract structured resume details from the following text:

            {text}

            Ensure structured formatting, correct duration calculations, and no missing fields.
            """

            # Call GPT Service
            structured_data = await self.gpt_service.extract_with_prompts(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                response_schema=ResumeSchema
            )

            return structured_data  

        except Exception as e:
            logger.error(f"Error parsing resume file '{filename}': {str(e)}", exc_info=True)
            raise
