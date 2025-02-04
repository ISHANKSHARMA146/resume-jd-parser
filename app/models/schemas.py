from pydantic import BaseModel, Field
from typing import List, Optional

# ===== Resume Parsing Schemas =====

class Education(BaseModel):
    degree: str = Field(..., description="Degree obtained by the candidate.")
    institution: str = Field(..., description="Institution where the candidate studied.")
    duration: str = Field(..., description="Calculated duration of the education in years or months.")
    cgpa: Optional[str] = Field(None, description="CGPA or percentage obtained by the candidate.")

class Experience(BaseModel):
    company: str = Field(..., description="Company where the candidate worked.")
    role: str = Field(..., description="Job role or title of the candidate.")
    duration: str = Field(..., description="Duration of the work experience in years or months.")
    description: str = Field(..., description="Brief description of responsibilities.")
    location: str = Field(..., description="Location of the company.")
    skills: List[str] = Field(..., description="Skills gained or used in this role.")
    tasks: List[str] = Field(..., description="Key tasks performed in this role.")

class ResumeSchema(BaseModel):
    candidate_name: str = Field(..., description="Full name of the candidate.")
    email_address: str = Field(..., description="Email address of the candidate.")
    phone_number: str = Field(..., description="Phone number of the candidate.")
    skills: List[str] = Field(..., description="List of extracted skills.")
    languages: Optional[List[str]] = Field(None, description="List of languages known by the candidate.")
    educations: List[Education] = Field(..., description="List of educational qualifications.")
    total_education_duration: str = Field(..., description="Total education duration calculated in years and/or months.")
    experiences: List[Experience] = Field(..., description="List of work experiences.")
    total_experience: str = Field(..., description="Total work experience duration calculated in years and/or months.")
    social_urls: Optional[List[str]] = Field(None, description="List of candidate's social URLs (LinkedIn, GitHub, etc.).")

# ===== Job Description Parsing Schemas =====

class JobDescriptionSchema(BaseModel):
    job_title: str = Field(..., description="Title of the job position.")
    job_description: str = Field(..., description="Full job description text.")
    required_skills: List[str] = Field(..., description="List of required skills for the job.")
    min_work_experience: Optional[str] = Field(None, description="Minimum work experience required for the job.")

