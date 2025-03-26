from io import BytesIO
from app.services.gpt_service import GPTService
from app.services.resume_extraction import ResumeParser
from app.utils.logger import Logger
from app.models.schemas import ATSResumeSchema  # Refined ATS resume schema

logger = Logger(__name__).get_logger()

class ResumeGenerationService:
    """
    Service for generating an ATS optimized resume.
    
    Provides two functions:
      1. generate_resume_from_upload: Takes an uploaded resume, extracts details, 
         enhances them, and generates a resume.
      2. generate_resume_from_form: Takes manual candidate data, enhances it, 
         and generates a resume.
    
    The output is returned as HTML. Client-side conversion to PDF or DOCX is handled on the frontend.
    """
    def __init__(self):
        logger.info("ResumeGenerationService initialized successfully.")
        self.gpt_service = GPTService()
        self.resume_parser = ResumeParser()

    async def generate_resume_from_upload(self, file_buffer: BytesIO, filename: str, output_format: str = "html") -> bytes:
        """
        1. Parse the resume to get extracted_data.
        2. Call GPT with a detailed system prompt and the ATSResumeSchema.
        3. Retrieve the final HTML from the 'formatted_resume' field.
        4. Always return the HTML resume as bytes.
        """
        # Step 1: Extract candidate data from the uploaded resume.
        extracted_data = await self.resume_parser.parse_resume(file_buffer, filename)

        # Step 2: Use a detailed, in-depth system prompt for ATS optimization.
        system_prompt = """
You are an expert resume writer with a deep understanding of Applicant Tracking Systems (ATS). Your task is to transform raw candidate details (extracted from an existing resume) into a perfect, high-scoring ATS-friendly resume.

Follow these guidelines STRICTLY:
1. USE ONLY THE PROVIDED DATA – do NOT invent or add any information beyond what is present.
2. REPHRASE and reformat the existing information to improve clarity and ensure high ATS compatibility.
3. Use strong action verbs, industry-specific keywords, and precise phrasing to target an ATS score of 90+ out of 100.
4. FORMAT THE OUTPUT IN HTML using these rules:
   - Candidate Name: Prominently displayed and center aligned.
   - Dates (employment/education): Right aligned.
   - Section Headings (e.g., "Professional Summary", "Work Experience", "Education"): Left aligned.
   - Body Text: Left aligned.
   - Lists: Use bullet points for achievements and skills.
5. The final resume must include these sections:
   - contact_information: An HTML snippet containing the candidate’s name (centered), email, phone, and links.
   - professional_summary: A powerful, concise HTML summary.
   - work_experiences: An array of objects (each with company, role, duration with dates right aligned, and achievements as bullet points in HTML).
   - education: An array of objects (each with institution, degree, dates right aligned, and description in HTML).
   - skills: An array of strings representing the candidate’s skills.
   - certifications: An array of strings (if available).
   - additional_sections: An object mapping section titles to HTML content (if provided).
   - formatted_resume: The complete final HTML resume that integrates all the above sections following the specified alignment and formatting rules.
6. The resume must only use the provided data without adding any extraneous or fictional details.
Return strictly valid JSON matching the ATSResumeSchema.
"""

        # Step 3: Build the user prompt using the extracted candidate data.
        user_prompt = f"Candidate Data: {extracted_data}"
        ats_resume = await self.gpt_service.extract_with_prompts(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_schema=ATSResumeSchema
        )

        # Step 4: Retrieve the final HTML from 'formatted_resume'
        if isinstance(ats_resume, dict) and "formatted_resume" in ats_resume:
            final_html = ats_resume["formatted_resume"]
        else:
            final_html = str(ats_resume)

        # Step 5: Always return the HTML (client handles PDF/DOCX conversion)
        return final_html.encode("utf-8")

    async def generate_resume_from_form(self, candidate_data: dict, output_format: str = "html") -> bytes:
        """
        1. Use the manually entered candidate data.
        2. Call GPT with a detailed system prompt and the ATSResumeSchema.
        3. Retrieve the final HTML from the 'formatted_resume' field.
        4. Always return the HTML resume as bytes.
        """
        system_prompt = """
You are an expert resume writer with in-depth knowledge of ATS requirements.
You will receive candidate data in JSON format provided by the candidate. Your task is to optimize this data into a professional, high-scoring ATS-friendly resume.

Follow these detailed instructions:
1. USE ONLY THE PROVIDED DATA – do NOT add any new information.
2. REPHRASE and enhance the provided data to improve clarity and ATS compatibility, using strong action verbs and relevant keywords.
3. FORMAT THE OUTPUT IN HTML with these rules:
   - Candidate Name: Center aligned and prominently displayed.
   - Dates: Right aligned.
   - Section Headings and Body Text: Left aligned.
   - Use bullet points for lists.
4. Include the following sections:
   - contact_information: HTML snippet with candidate’s name, email, phone, etc.
   - professional_summary: A concise HTML summary.
   - work_experiences: Array of objects with 'company', 'role', 'duration' (dates right aligned), and 'achievements' (bullet points in HTML).
   - education: Array of objects with 'institution', 'degree', 'dates' (right aligned), and 'description' (HTML).
   - skills: Array of strings.
   - certifications: Array of strings (if available).
   - additional_sections: Object mapping section titles to HTML content (if provided).
   - formatted_resume: The complete final HTML resume that integrates all the sections with proper formatting.
5. Do not add any information that is not provided.
Return strictly valid JSON that conforms to the ATSResumeSchema.
"""
        user_prompt = f"Candidate Data: {candidate_data}"
        ats_resume = await self.gpt_service.extract_with_prompts(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_schema=ATSResumeSchema
        )

        if isinstance(ats_resume, dict) and "formatted_resume" in ats_resume:
            final_html = ats_resume["formatted_resume"]
        else:
            final_html = str(ats_resume)

        return final_html.encode("utf-8")
