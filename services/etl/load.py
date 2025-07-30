import json

from typing import Any, Dict, List

from services.etl.abstraction import IEtlService
from start_utils import logger


class ETLLoadService(IEtlService):
    """
    ETL load service
    """
    def __init__(self, file_path: str):
        super().__init__()
        self.logger = logger
        self.file_path = file_path

    def run(self) -> List[Dict[str, Any]]:
        """
        Run the ETL load service
        """
        self.logger.info(f"Loading data from {self.file_path}...")
        with open(self.file_path, "r") as file:
            data = json.load(file)
        self.logger.info(f"Loaded {len(data)} profiles")
        return data
