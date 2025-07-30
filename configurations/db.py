import json

from dtos.configurations.db import DBConfigurationDTO

from start_utils import logger


class DBConfiguration:
    """
    Singleton loader and manager for database configuration.
    Loads configuration from config/db/config.json.
    """
    _instance = None

    def __new__(cls):

        if cls._instance is None:
            cls._instance = super(DBConfiguration, cls).__new__(cls)
            cls._instance.config = {}
            cls._instance.load_config()
        return cls._instance

    def load_config(self):
        """
        Load database configuration from JSON file.
        Logs if the file is not found or cannot be decoded.
        """
        try:

            with open("config/db/config.json", "r") as file:
                self.config = json.load(file)
            logger.debug("DB config loaded successfully.")

        except FileNotFoundError:
            logger.debug("DB config file not found.")

        except json.JSONDecodeError:
            logger.debug("Error decoding DB config file.")

    def get_config(self):
        """
        Return the database configuration as a DTO.
        """
        return DBConfigurationDTO(
            user_name=self.config.get("user_name"),
            password=self.config.get("password"),
            host=self.config.get("host"),
            port=self.config.get("port"),
            database=self.config.get("database"),
            connection_string=self.config.get("connection_string"),
        )
