from pydantic import BaseModel, Field
from typing import List, Optional


class DurationDto(BaseModel):
    years: int = Field(..., description="Number of years")
    months: int = Field(..., description="Number of months")


class ExperienceDto(BaseModel):
    key: str = Field(..., description="Unique identifier for the experience")
    logo: Optional[str] = Field(None, description="Logo of the company or organization")
    title: Optional[str] = Field(None, description="Job title or position held")
    description: Optional[str] = Field(None, description="Description of responsibilities")
    date_start: Optional[str] = Field(None, description="Start date of the role")
    date_end: Optional[str] = Field(None, description="End date of the role")
    skills: Optional[List[str]] = Field(None, description="Skills gained during the experience")
    certifications: Optional[List[str]] = Field(None, description="Certifications related to the role")
    courses: Optional[List[str]] = Field(None, description="Courses completed during the role")
    tasks: Optional[List[str]] = Field(None, description="Key tasks performed in the role")
    languages: Optional[List[str]] = Field(None, description="Languages used or known in the role")
    interests: Optional[List[str]] = Field(None, description="Personal interests")
    company: str = Field(..., description="Company name where the experience took place")


class EducationDto(BaseModel):
    key: Optional[str] = Field(None, description="Unique identifier for education")
    logo: Optional[str] = Field(None, description="Logo of the educational institution")
    title: Optional[str] = Field(None, description="Degree or qualification")
    description: Optional[str] = Field(None, description="Description of the program or course")
    date_start: Optional[str] = Field(None, description="Start date of the education")
    date_end: Optional[str] = Field(None, description="End date of the education")
    skills: Optional[List[str]] = Field(None, description="Skills learned during the course")
    certifications: Optional[List[str]] = Field(None, description="Certifications related to the education")
    courses: Optional[List[str]] = Field(None, description="Courses completed during education")
    tasks: Optional[List[str]] = Field(None, description="Tasks or projects undertaken during education")
    languages: Optional[List[str]] = Field(None, description="Languages known during education")
    interests: Optional[List[str]] = Field(None, description="Personal interests during education")
    school: str = Field(..., description="Name of the school or university")


class SocialUrlDto(BaseModel):
    type: Optional[str] = Field(None, description="Type of social link (LinkedIn, GitHub, etc.)")
    url: Optional[str] = Field(None, description="URL to the social profile")


class LanguageItemDto(BaseModel):
    name: Optional[str] = Field(None, description="Name of the language known")


class SkillsDto(BaseModel):
    primary_skills: Optional[List[str]] = Field(None, description="Primary skills of the candidate")
    secondary_skills: Optional[List[str]] = Field(None, description="Secondary skills of the candidate")


class ResumeSchema(BaseModel):
    candidate_name: Optional[str] = Field(None, description="Full name of the candidate")
    email_address: Optional[str] = Field(None, description="Email address")
    phone_number: Optional[str] = Field(None, description="Phone number")
    work_experience: Optional[DurationDto] = Field(None, description="Work experience duration")
    educations_duration: Optional[DurationDto] = Field(None, description="Total education duration")
    experiences: Optional[List[ExperienceDto]] = Field(None, description="List of work experiences")
    educations: Optional[List[EducationDto]] = Field(None, description="List of educational qualifications")
    social_urls: Optional[List[SocialUrlDto]] = Field(None, description="List of social media URLs")
    languages: Optional[List[LanguageItemDto]] = Field(None, description="List of languages known")
    skills: Optional[SkillsDto] = Field(None, description="Skills information")


class JobDescriptionSchema(BaseModel):
    job_title: str = Field(..., description="Job title for the position")
    job_description: str = Field(..., description="Full job description text")
    required_skills: Optional[List[str]] = Field(None, description="List of required skills for the job")
    min_work_experience: Optional[str] = Field(None, description="Minimum work experience required for the job")

class JobDescriptionSchemaBase(BaseModel):
    response: JobDescriptionSchema = Field(..., description="Structured job description data")
    filename: Optional[str] = Field(None, description="Name of the uploaded file")
