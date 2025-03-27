import os
from io import BytesIO
from app.services.gpt_service import GPTService
from app.services.resume_extraction import ResumeParser
from app.utils.logger import Logger
from app.models.schemas import ATSResumeSchema  # Refined ATS resume schema

logger = Logger(__name__).get_logger()

def load_universal_prompt() -> str:
    """Load the universal enhancement prompt from 'templates/universal_prompt.txt'."""
    path = os.path.join("templates", "universal_prompt.txt")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error loading universal prompt: {str(e)}", exc_info=True)
        raise

def load_system_prompt(template_id: int) -> str:
    """
    Load the template-specific system prompt file for the given template_id.
    Files should be stored as 'templates/system_prompt_{template_id}.txt'
    """
    path = os.path.join("templates", f"system_prompt_{template_id}.txt")
    try:
        with open(path, "r", encoding="utf-8") as f:
            prompt = f.read()
        return prompt
    except Exception as e:
        logger.error(f"Error loading system prompt for template {template_id}: {str(e)}", exc_info=True)
        raise

def load_html_wrapper(template_id: int) -> str:
    """
    Load the HTML wrapper file for the given template_id.
    Files should be stored as 'templates/html_wrapper_{template_id}.html'
    The file must include a placeholder {{resume_content}} where the generated resume will be inserted.
    """
    path = os.path.join("templates", f"html_wrapper_{template_id}.html")
    try:
        with open(path, "r", encoding="utf-8") as f:
            html_wrapper = f.read()
        return html_wrapper
    except Exception as e:
        logger.error(f"Error loading HTML wrapper for template {template_id}: {str(e)}", exc_info=True)
        raise

class ResumeGenerationService:
    """
    Service for generating an ATS optimized resume.
    
    Provides two functions:
      1. generate_resume_from_upload: Takes an uploaded resume, extracts details, enhances them, and generates a resume.
      2. generate_resume_from_form: Takes manual candidate data, enhances it, and generates a resume.
    
    This backend service now supports multiple templates by accepting a template_id (1 to 5).
    Based on the template_id, the corresponding system prompt and HTML wrapper are loaded from the "templates" folder.
    """
    def __init__(self):
        logger.info("ResumeGenerationService initialized successfully.")
        self.gpt_service = GPTService()
        self.resume_parser = ResumeParser()

    async def generate_resume_from_upload(self, file_buffer: BytesIO, filename: str, template_id: int = 1, output_format: str = "html") -> bytes:
        # Extract candidate data.
        extracted_data = await self.resume_parser.parse_resume(file_buffer, filename)
        
        # Load and combine universal and template-specific prompts.
        universal_prompt = load_universal_prompt()
        system_prompt = load_system_prompt(template_id)
        full_system_prompt = universal_prompt + "\n" + system_prompt

        # Build user prompt with candidate data.
        user_prompt = f"Candidate Data: {extracted_data}"
        ats_resume = await self.gpt_service.extract_with_prompts(
            system_prompt=full_system_prompt,
            user_prompt=user_prompt,
            response_schema=ATSResumeSchema
        )

        if isinstance(ats_resume, dict) and "formatted_resume" in ats_resume:
            resume_content = ats_resume["formatted_resume"]
        else:
            resume_content = str(ats_resume)

        html_wrapper = load_html_wrapper(template_id)
        full_html = html_wrapper.replace("{{resume_content}}", resume_content)
        return full_html.encode("utf-8")

    async def generate_resume_from_form(self, candidate_data: dict, template_id: int = 1, output_format: str = "html") -> bytes:
        """
        1. Use the manually provided candidate data.
        2. Load the system prompt for the given template_id.
        3. Call GPT with the loaded system prompt and candidate data using ATSResumeSchema.
        4. Retrieve the resume body content from the 'formatted_resume' field.
        5. Load the corresponding HTML wrapper and substitute the placeholder with the resume content.
        6. Return the final HTML resume as bytes.
        """
        # Step 1: Load system prompt.
        system_prompt = load_system_prompt(template_id)
        
        # Step 2: Build user prompt.
        user_prompt = f"Candidate Data: {candidate_data}"
        ats_resume = await self.gpt_service.extract_with_prompts(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_schema=ATSResumeSchema
        )
        
        # Step 3: Retrieve resume content.
        if isinstance(ats_resume, dict) and "formatted_resume" in ats_resume:
            resume_content = ats_resume["formatted_resume"]
        else:
            resume_content = str(ats_resume)
        
        # Step 4: Load HTML wrapper.
        html_wrapper = load_html_wrapper(template_id)
        full_html = html_wrapper.replace("{{resume_content}}", resume_content)
        
        # Step 5: Return final HTML as bytes.
        return full_html.encode("utf-8")
