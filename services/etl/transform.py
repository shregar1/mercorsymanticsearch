from typing import List

from dtos.services.etl.profile import ProfileData
from services.etl.abstraction import IEtlService

from start_utils import logger


class ETLTransformService(IEtlService):
    """
    ETL extraction service
    """
    def __init__(self):
        super().__init__()
        self.logger = logger

    def to_llm_text(self, profile: ProfileData) -> str:
        data = profile.model_dump()
        return "\n".join([f"{k.capitalize()}: {v}" for k, v in data.items()])

    def run(self, profiles: List[ProfileData]):
        """
        Run the ETL transform service
        """
        self.logger.info(f"Transforming {len(profiles)} profiles...")
        texts = {
            profile.profile_id: self.to_llm_text(profile)
            for profile in profiles
        }
        self.logger.info(f"Transformed {len(texts)} profiles...")
        return texts
