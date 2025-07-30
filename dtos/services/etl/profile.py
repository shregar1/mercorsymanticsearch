from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class ExperiencePosition(BaseModel):
    """
    Detailed information about a specific position held within a company.
    """
    title: Optional[str] = Field(
        None,
        description="The title of the position held."
    )
    startDate: Optional[str] = Field(
        None,
        description=(
            "The start date of the position "
            "(e.g., 'YYYY-MM-DDTHH:MM:SS.sssZ')."
        )
    )
    endDate: Optional[str] = Field(
        None,
        description=(
            "The end date of the position (e.g., 'YYYY-MM-DDTHH:MM:SS.sssZ'). "
            "Null if current."
        )
    )
    description: Optional[str] = Field(
        None,
        description=(
            "A detailed description of the responsibilities and achievements "
            "in this position."
        )
    )
    yearsOfWorkExperience: Optional[float] = Field(
        None,
        description=(
            "The duration of this specific position in years."
        )
    )


class Experience(BaseModel):
    """
    Detailed information about a work experience entry,
    including company and positions.
    """
    company: Optional[str] = Field(
        None,
        description="The name of the company where the experience was gained."
    )
    positions: List[ExperiencePosition] = Field(
        default_factory=list,
        description="A list of positions held at this company."
    )
    yearsOfWorkExperience: Optional[float] = Field(
        None,
        description=(
            "The total duration of work experience at this company in years."
        )
    )
    prestige_score: Optional[float] = Field(
        None,
        description=(
            "A numerical score indicating the prestige of the "
            "company or experience."
        )
    )


class EducationDegree(BaseModel):
    """
    Detailed information about an educational degree.
    """
    school: Optional[str] = Field(
        None,
        description=(
            "The name of the educational institution."
        )
    )
    degree: Optional[str] = Field(
        None,
        description=(
            "The type of degree obtained (e.g., 'Bachelor\'s', 'Doctorate')."
        )
    )
    fieldOfStudy: Optional[str] = Field(
        None,
        description=(
            "The specific field of study "
            "(e.g., 'Molecular Genetics', 'Computer Science')."
        )
    )
    startDate: Optional[str] = Field(
        None,
        description=(
            "The start date of the education period."
        )
    )
    endDate: Optional[str] = Field(
        None,
        description=(
            "The end date of the education period."
        )
    )
    prestige_score: Optional[float] = Field(
        None,
        description=(
            "A numerical score indicating the prestige of "
            "the educational institution or degree."
        )
    )
    subject: Optional[str] = Field(
        None,
        description=(
            "The subject of the degree, often similar to fieldOfStudy."
        )
    )


class ProfileData(BaseModel):
    """
    Pydantic model for structuring comprehensive professional profile data.

    This model is designed to be used with Large Language Models (LLMs)
    to extract and represent detailed information from professional profiles
    in a structured format. Each field includes a detailed description to guide
    the LLM in accurate data extraction.
    """

    profile_id: str = Field(
        ...,
        description=(
            "A unique identifier for the professional profile, "
            "typically derived from the profile URL or a system-generated ID."
        )
    )
    name: str = Field(
        ...,
        description=(
            "The full name of the individual as displayed on "
            "their professional profile."
        )
    )
    current_title: Optional[str] = Field(
        None,
        description=(
            "The current professional title or headline of the "
            "individual. Can be null if not specified."
        )
    )
    current_company: Optional[str] = Field(
        None,
        description=(
            "The name of the current company or organization the "
            "individual is associated with. Can be null if not specified."
        )
    )
    profile_location: Optional[str] = Field(
        None,
        description=(
            "The primary geographical location of the individual, "
            "as stated on their profile "
            "(e.g., 'San Francisco Bay Area', "
            "'London, England, United Kingdom')."
            "Can be null if not specified."
        )
    )
    experience_years: Optional[float] = Field(
        None,
        description=(
            "The total number of years of professional experience the "
            "individual has. This should be a float. "
            "Can be null if not derivable."
        )
    )
    experiences: List[Experience] = Field(
        default_factory=list,
        description=(
            "A detailed list of all work experiences, including "
            "companies and positions held."
        )
    )
    skills: List[str] = Field(
        default_factory=list,
        description=(
            "A list of key skills and endorsements listed on the "
            "profile (e.g., 'Project Management', 'Python', 'Data Analysis'). "
            "Should be an array of strings."
        )
    )
    education_details: List[EducationDegree] = Field(
        default_factory=list,
        description=(
            "A detailed list of all educational degrees obtained, "
            "including school, degree, and field of study."
        )
    )
    highest_education_level: Optional[str] = Field(
        None,
        description=(
            "The highest level of education attained "
            "(e.g., 'Doctorate', 'Master\'s', 'Bachelor\'s')."
        )
    )
    industry: Optional[str] = Field(
        None,
        description=(
            "The primary industry the individual or their current "
            "company operates in "
            "(e.g., 'Information Technology', 'Finance')."
            "Can be null if not specified."
        )
    )
    summary: Optional[str] = Field(
        None,
        description=(
            "A concise summary or 'About' section text from the "
            "profile, highlighting professional goals, achievements, "
            "and expertise. Can be null if not specified."
        )
    )
    connections: Optional[int] = Field(
        None,
        description=(
            "The number of connections or network size the profile has. "
            "This should be an integer. "
            "Often displayed as '500+' if over 500. "
            "If '500+', infer as 501 or a similar representative value. "
            "Can be null if not derivable."
        )
    )
    raw_text: str = Field(
        ...,
        description=(
            "The complete raw text content of the professional profile, "
            "suitable for embedding or further natural language processing. "
            "This field should contain all extracted text from the profile."
        )
    )
    work_locations: List[str] = Field(
        default_factory=list,
        description=(
            "A list of distinct geographical locations where the individual "
            "has worked, extracted from experience details."
        )
    )
    study_locations: List[str] = Field(
        default_factory=list,
        description=(
            "A list of distinct geographical locations where the individual "
            "has studied, extracted from education details."
        )
    )

    model_config = ConfigDict(extra='allow')
