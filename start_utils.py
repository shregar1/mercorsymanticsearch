"""
Startup utilities for CalCount: loads configuration, environment variables,
and initializes core services (DB, Redis, LLM, logging).
"""
import os
import sys
import openai
import voyageai

from dotenv import load_dotenv
from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from configurations.db import DBConfiguration, DBConfigurationDTO

logger.add(
    sys.stderr,
    colorize=True,
    format=(
        "<green>{time:MMMM-D-YYYY}</green> | <black>{time:HH:mm:ss}</black> | "
        "<level>{level}</level> | <cyan>{message}</cyan> | "
        "<magenta>{name}:{function}:{line}</magenta> | "
        "<yellow>{extra}</yellow>"
    ),
)

# Load environment variables from .env file
logger.info("Loading .env file and environment variables")
load_dotenv()

logger.info("Loading Configurations")
db_configuration: DBConfigurationDTO = DBConfiguration().get_config()
logger.info("Loaded Configurations")

# Access environment variables
logger.info("Loading environment variables")
APP_NAME: str = os.environ.get("APP_NAME")
SECRET_KEY: str = os.getenv("SECRET_KEY")
GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY")
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
VOYAGEAI_API_KEY: str = os.getenv("VOYAGEAI_API_KEY")
logger.info("Loaded environment variables")

logger.info("Initializing OpenAI client")
openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
if not openai_client:
    raise RuntimeError("OpenAI client not found")

logger.info("Initialized OpenAI client")

logger.info("Initializing VoyageAI client")
voyageai_client: voyageai.Client = voyageai.Client(api_key=VOYAGEAI_API_KEY)
if not voyageai_client:
    raise RuntimeError("VoyageAI client not found")
logger.info("Initialized VoyageAI client")

logger.info("Initializing PostgreSQL database connection")
engine = create_engine(
    db_configuration.connection_string.format(
        user_name=db_configuration.user_name,
        password=db_configuration.password,
        host=db_configuration.host,
        port=db_configuration.port,
        database=db_configuration.database,
    )
)
Session = sessionmaker(bind=engine)
db_session = Session()
logger.info("Initialized PostgreSQL database connection")
