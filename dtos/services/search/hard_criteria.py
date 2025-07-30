from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class HardCriteria(BaseModel):
    """
    Pydantic model for defining hard filtering criteria for
    professional profiles,
    typically used in Retrieval-Augmented Generation (RAG) or search contexts.

    This model allows specifying strict requirements for filtering profiles
    based on
    various professional attributes.
    """

    min_experience: Optional[int] = Field(
        None,
        description=(
            "Minimum number of years of professional experience required. "
            "Profiles with less experience will be filtered out."
        )
    )
    max_experience: Optional[int] = Field(
        None,
        description=(
            "Maximum number of years of professional experience allowed. "
            "Profiles with more experience will be filtered out."
        )
    )
    required_skills: Optional[List[str]] = Field(
        None,
        description=(
            "A list of skills that a profile MUST possess. "
            "Profiles missing any of these skills will be filtered out."
        )
    )
    excluded_skills: Optional[List[str]] = Field(
        None,
        description=(
            "A list of skills that a profile MUST NOT possess. "
            "Profiles having any of these skills will be filtered out."
        )
    )
    locations: Optional[List[str]] = Field(
        None,
        description=(
            "A list of geographical locations. "
            "Profiles must be located in one of these areas to be included."
        )
    )
    industries: Optional[List[str]] = Field(
        None,
        description=(
            "A list of industries. "
            "Profiles must belong to one of these industries to be included."
        )
    )
    companies: Optional[List[str]] = Field(
        None,
        description=(
            "A list of companies. "
            "Profiles must be associated with one of these companies "
            "to be included."
        )
    )
    min_connections: Optional[int] = Field(
        None,
        description=(
            "Minimum number of connections or network size required for "
            "a profile. "
            "Profiles with fewer connections will be filtered out."
        )
    )
    education_keywords: Optional[List[str]] = Field(
        None,
        description=(
            "A list of keywords that must be present in the education field "
            "of a profile (e.g., 'MBA', 'PhD', 'Computer Science')."
        )
    )

    model_config = ConfigDict(extra='allow')
