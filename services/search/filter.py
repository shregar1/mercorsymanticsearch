from ast import Dict
import json
from constants.prompt import Prompt
from dtos.services.etl.profile import ProfileData
from dtos.services.search.hard_criteria import HardCriteria
from services.llm.generate import LLMGenerateService
from services.search.abstraction import ISearchService


class FilterProfilesService(ISearchService):
    def __init__(self):
        self.llm_generate_service = LLMGenerateService()

    def generate_prompt(
        self,
        job_title: str,
        job_description: str,
        profile: ProfileData,
        hard_criteria: HardCriteria,
        soft_criteria={},
    ) -> str:
        prompt = Prompt.LLM_ANALYSIS_PROMPT.format(
            profile=profile,
            hard_criteria=hard_criteria,
            soft_criteria=soft_criteria,
            job_title=job_title,
            job_description=job_description,
        )
        return prompt

    def run(
        self,
        job_title: str,
        job_description: str,
        profile: ProfileData,
        hard_criteria: HardCriteria,
        soft_criteria={},
    ) -> Dict:

        prompt = self.generate_prompt(
            job_title=job_title,
            job_description=job_description,
            profile=profile,
            hard_criteria=hard_criteria,
            soft_criteria=soft_criteria,
        )
        response = self.llm_generate_service.run(prompt)

        # Parse the JSON response from the LLM
        try:
            response_dict = json.loads(response)
        except json.JSONDecodeError:
            # If JSON parsing fails, return a default response
            response_dict = {
                "overall_score": 0,
                "criterion_breakdown": {},
                "profile": profile,
            }

        return {
            "overall_score": response_dict.get("overall_score"),
            "criterion_breakdown": response_dict.get("criterion_breakdown"),
            "profile": profile,
        }
