import uuid
import tqdm
from sqlalchemy.orm import Session
from typing import Any, Dict, List

from dtos.services.etl.profile import (
    ProfileData,
    Experience,
    ExperiencePosition,
    EducationDegree
)

from models.education import (
    Education as EducationModel
)
from models.experience import (
    Experience as ExperienceModel
)
from models.experience_position import (
    ExperiencePosition as ExperiencePositionModel
)
from models.profile import (
    Profile as ProfileModel
)

from repositories.education import EducationRepository
from repositories.experience import ExperienceRepository
from repositories.experience_position import ExperiencePositionRepository
from repositories.profile import ProfileRepository

from services.etl.abstraction import IEtlService

from start_utils import logger


class ETLExtractionService(IEtlService):

    def __init__(self, session: Session) -> None:
        super().__init__()
        self.session = session
        self.profile_repository = ProfileRepository(self.session)
        self.education_repository = EducationRepository(self.session)
        self.experience_repository = ExperienceRepository(self.session)
        self.experience_position_repository = ExperiencePositionRepository(
            self.session,
        )
        self.logger = logger

    def get_start_date(self, exp):
        if exp.get("positions"):
            start_date = exp["positions"][-1].get("startDate")
            return start_date or ""  # Always return a string
        return ""

    def build_profile_data_from_json(
        self,
        data: Dict[str, Any]
    ) -> ProfileData:
        """
        Constructs a ProfileData Pydantic model instance from a raw JSON
        data dictionary, extracting as much concrete detail as possible.

        Args:
            data (Dict[str, Any]): A dictionary containing the raw
            professional profile data.

        Returns:
            ProfileData: An instance of the ProfileData Pydantic model with()
            granular details.
        """
        profile_id = (
            data.get("personId")
            or data.get("linkedinId")
            or data.get("_id", {}).get("$oid", "")
        )
        name = data.get("name", "")
        current_title = data.get("headline")

        current_company = None
        parsed_experience: List[Experience] = []
        work_locations_set = set()
        if data.get("experience"):

            sorted_experience = sorted(
                data["experience"],
                key=self.get_start_date,
                reverse=True
            )

            if sorted_experience:
                latest_exp_entry = sorted_experience[0]
                current_company = latest_exp_entry.get("company")
                if latest_exp_entry.get("positions"):
                    current_position = latest_exp_entry["positions"][-1]
                    current_title = (
                        current_position.get("title") or current_title
                    )

            for exp_entry in data["experience"]:
                positions_list: List[ExperiencePosition] = []
                if exp_entry.get("positions"):
                    for pos in exp_entry["positions"]:
                        years_of_work_experience = (
                            pos.get("yearsOfWorkExperience")
                        )
                        positions_list.append(ExperiencePosition(
                            title=pos.get("title"),
                            startDate=pos.get("startDate"),
                            endDate=pos.get("endDate"),
                            description=pos.get("description"),
                            yearsOfWorkExperience=years_of_work_experience
                        ))
                parsed_experience.append(Experience(
                    company=exp_entry.get("company"),
                    positions=positions_list,
                    yearsOfWorkExperience=(
                        exp_entry.get("yearsOfWorkExperience")
                    ),
                    prestige_score=exp_entry.get("prestige_score")
                ))
                # Attempt to extract work location from rerankSummary
                # if company is mentioned
                if exp_entry.get("company") and data.get("rerankSummary"):
                    # This is a heuristic, might need more robust parsing for
                    # real-world data
                    if (
                        f"Company: {exp_entry['company']}"
                        in data["rerankSummary"]
                    ):
                        # Look for location near the company name in
                        # rerankSummary
                        # This is a very basic attempt and might not capture
                        # all cases.
                        # A more advanced approach would involve NLP or regex
                        # on the raw_text.
                        pass  # Current JSON doesn't provide per-company
                        # location easily.

        profile_location = None
        if data.get("rerankSummary"):
            for line in data["rerankSummary"].split('\n'):
                if line.startswith("Location:"):
                    profile_location = line.replace("Location:", "").strip()
                    break

        if profile_location:
            work_locations_set.add(profile_location)

        experience_years = (
            float(data.get("yearsOfWorkExperience"))
            if data.get("yearsOfWorkExperience") is not None
            else None
        )
        skills = data.get("skills", [])

        parsed_education_details: List[EducationDegree] = []
        highest_education_level = (
            data.get("education", {}).get("highest_level")
        )
        study_locations_set = set()

        if data.get("education") and data["education"].get("degrees"):
            for degree_info in data["education"]["degrees"]:
                parsed_education_details.append(EducationDegree(
                    school=degree_info.get("school"),
                    degree=degree_info.get("degree"),
                    fieldOfStudy=degree_info.get("fieldOfStudy"),
                    startDate=degree_info.get("startDate"),
                    endDate=degree_info.get("endDate"),
                    prestige_score=degree_info.get("prestige_score"),
                    subject=degree_info.get("subject")
                ))
                # Attempt to extract study location from rerankSummary if
                # school is mentioned
                # This is a heuristic, might need more robust parsing for
                # real-world data
                if degree_info.get("school") and data.get("rerankSummary"):
                    if (
                        f"Degree: {degree_info['degree']} from "
                        f"{degree_info['school']}"
                        in data["rerankSummary"]
                    ):
                        # The provided JSON's rerankSummary has "Location:
                        # Buffalo, New York, United States" at the end,
                        # which is associated with the latest education.
                        pass  # Current JSON doesn't provide per-school
                        # location easily within degrees.

        # If the main profile_location is derived from the end of
        # rerankSummary, and it's likely a study location
        if (
            profile_location
            and "Education:" in data.get("rerankSummary", "")
            and data.get("rerankSummary", "").endswith(profile_location)
        ):
            study_locations_set.add(profile_location)

        industry = None

        summary = None
        if data.get("rerankSummary"):
            summary_lines = []
            in_about_section = False
            for line in data["rerankSummary"].split('\n'):
                if line.startswith("About:"):
                    in_about_section = True
                    summary_lines.append(line.replace("About:", "").strip())
                    continue
                if (
                    in_about_section
                    and not line.strip().startswith(
                        ("Experience:", "Education:")
                    )
                ):
                    summary_lines.append(line.strip())
                elif in_about_section:
                    break
            if summary_lines:
                summary = " ".join(summary_lines).strip()

        connections = None
        raw_text = data.get("rerankSummary", "")

        return ProfileData(
            profile_id=profile_id,
            name=name,
            current_title=current_title,
            current_company=current_company,
            profile_location=profile_location,
            experience_years=experience_years,
            experience=parsed_experience,
            skills=skills,
            education_details=parsed_education_details,
            highest_education_level=highest_education_level,
            industry=industry,
            summary=summary,
            connections=connections,
            raw_text=raw_text,
            work_locations=list(work_locations_set),
            study_locations=list(study_locations_set)
        )

    def run(self, profiles: List[Dict[str, Any]]):
        """
        Extracts profile data from a list of profiles and creates corresponding
        models in the database.

        Args:
            profiles (List[Dict[str, Any]]): A list of profile dictionaries,
            each containing LinkedIn profile data.
        """
        self.logger.info(
            "Extracting profiles: {}", len(profiles)
        )

        profiles_data: List[Dict[str, Any]] = []
        for profile in tqdm.tqdm(profiles):
            profile_data = self.build_profile_data_from_json(profile)
            education_details = profile_data.education_details

            for education_detail in education_details:
                education = EducationModel(
                    urn=uuid.uuid4(),
                    profile_id=profile_data.profile_id,
                    school=education_detail.school,
                    degree=education_detail.degree,
                    fieldOfStudy=education_detail.fieldOfStudy,
                    startDate=education_detail.startDate,
                    endDate=education_detail.endDate,
                    prestige_score=education_detail.prestige_score,
                    subject=education_detail.subject
                )
                self.education_repository.create(
                    education=education,
                )

            experiences: List[Experience] = profile_data.experiences
            for experience in experiences:

                experience = ExperienceModel(
                    urn=uuid.uuid4(),
                    profile_id=profile_data.profile_id,
                    company=(
                        experience.company.lower()
                        if experience.company
                        else None
                    ),
                    yearsOfWorkExperience=experience.yearsOfWorkExperience,
                    prestige_score=experience.prestige_score,
                )
                self.experience_repository.create(
                    experience=experience,
                )

                positions: List[ExperiencePosition] = experience.positions
                positions_list: List[ExperiencePositionModel] = []
                for position in positions:
                    experience_position = ExperiencePositionModel(
                        urn=uuid.uuid4(),
                        experience_id=experience.id,
                        title=(
                            position.title.lower()
                            if position.title
                            else None
                        ),
                        startDate=position.startDate,
                        endDate=position.endDate,
                        description=(
                            position.description.lower()
                            if position.description
                            else None
                        ),
                        yearsOfWorkExperience=position.yearsOfWorkExperience,
                    )
                    self.experience_position_repository.create(
                        position=experience_position,
                    )
                    positions_list.append(experience_position)

            if profile_data:
                profile = ProfileModel(
                    urn=profile_data.profile_id,
                    name=profile_data.name,
                    current_title=(
                        profile_data.current_title.lower()
                        if profile_data.current_title
                        else None
                    ),
                    current_company=(
                        profile_data.current_company.lower()
                        if profile_data.current_company
                        else None
                    ),
                    profile_location=(
                        profile_data.profile_location.lower()
                        if profile_data.profile_location
                        else None
                    ),
                    experience_years=profile_data.experience_years,
                    skills=(
                        [skill.lower() for skill in profile_data.skills]
                        if profile_data.skills
                        else None
                    ),
                    highest_education_level=(
                        profile_data.highest_education_level.lower()
                        if profile_data.highest_education_level
                        else None
                    ),
                    industry=(
                        profile_data.industry.lower()
                        if profile_data.industry
                        else None
                    ),
                    summary=(
                        profile_data.summary.lower()
                        if profile_data.summary
                        else None
                    ),
                    connections=profile_data.connections,
                    raw_text=(
                        profile_data.raw_text.lower()
                        if profile_data.raw_text
                        else None
                    ),
                    work_locations=(
                        [
                            location.lower()
                            for location in profile_data.work_locations
                        ]
                        if profile_data.work_locations
                        else None
                    ),
                )
                self.profile_repository.create(profile)

            profiles_data.append(profile_data)

        self.logger.info(
            "Profiles created: {}", len(profiles_data)
        )

        return profiles_data
