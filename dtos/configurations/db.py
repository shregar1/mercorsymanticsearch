"""
DTO for database configuration settings.
"""
from pydantic import BaseModel


class DBConfigurationDTO(BaseModel):
    """
    DTO for database configuration.
    Fields:
        user_name (str): Database username.
        password (str): Database password.
        host (str): Database host.
        port (int): Database port.
        database (str): Database name.
        connection_string (str): Full DB connection string.
    """
    user_name: str
    password: str
    host: str
    port: int
    database: str
    connection_string: str
