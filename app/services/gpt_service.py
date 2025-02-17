from openai import OpenAI
from app.utils.logger import Logger
from app.models.schemas import (
    ResumeSchema, 
    JobDescriptionSchema, 
    EnhancedJobDescriptionSchema, 
    CandidateProfileSchema, 
    JobDescriptionEnhancementResponse,
    ResumeScoringSchema,
    CandidateProfileSchemaList
)
from app.services.config_service import ConfigService
from typing import Dict, Any

# Initialize Logger
logger = Logger(__name__).get_logger()

class GPTService:
    """
    Service for interacting with OpenAI's GPT API to process resume and job description text.
    """
    def __init__(self):
        """
        Initializes the GPT service with the OpenAI API key.
        """
        try:
            config = ConfigService()
            self.openai_client = OpenAI(api_key=config.get_openai_key())
            logger.info("GPT service initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize GPT service: {str(e)}", exc_info=True)
            raise

    async def extract_with_prompts(
        self,
        system_prompt: str,
        user_prompt: str,
        response_schema: Any  # Keep response_schema unchanged
    ) -> Dict[str, Any]:
        """
        Extract structured information using GPT with custom prompts and schema.
        
        Args:
            system_prompt (str): System-level instructions for GPT.
            user_prompt (str): User-specific query for GPT processing.
            response_schema (Any): Expected schema for the response.

        Returns:
            Dict containing extracted structured information.
        """
        try:
            # Construct the messages
            messages = [
                {"role": "system", "content": f"{system_prompt}\n\nEnsure response follows the schema."},
                {"role": "user", "content": f"{user_prompt}"}
            ]

            # Make GPT API call
            response = self.openai_client.beta.chat.completions.parse(
                model="gpt-4o-mini",
                messages=messages,
                response_format=response_schema  # ✅ Keep response_schema unchanged
            )

            # Parse and return the structured response
            result = response.choices[0].message.parsed.dict()
            return result

        except Exception as e:
            logger.error(f"GPT extraction failed: {str(e)}", exc_info=True)
            raise Exception(f"GPT extraction failed: {str(e)}")
