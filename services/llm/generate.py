from services.llm.abstraction import ILLMService

from start_utils import logger, openai_client


class LLMGenerateService(ILLMService):

    def __init__(self):
        """
        Initialize the LLM generate service
        """
        super().__init__()
        self.logger = logger
        self.model = "gpt-4.1-nano"
        self.llm_model = openai_client

    def run(
        self,
        prompt: str,
    ) -> str:
        """
        Generate a response from the LLM
        """
        self.logger.info("Generating response from LLM")
        response = self.llm_model.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": prompt},
            ],
        )
        self.logger.info(f"Response from LLM: {response}")

        return response
