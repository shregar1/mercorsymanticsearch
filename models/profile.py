from sqlalchemy import (
    Column, String, Integer, Float, Text
)
from sqlalchemy.types import JSON

from models import Base


class Profile(Base):
    __tablename__ = "profile"

    id = Column(Integer, primary_key=True, autoincrement=True)
    urn = Column(String, nullable=False)
    name = Column(String, nullable=False)
    current_title = Column(String)
    current_company = Column(String)
    profile_location = Column(String)
    experience_years = Column(Float)
    skills = Column(JSON, default=[])
    highest_education_level = Column(String)
    industry = Column(String)
    summary = Column(Text)
    connections = Column(Integer)
    raw_text = Column(Text, nullable=False)
    work_locations = Column(JSON, default=[])
    study_locations = Column(JSON, default=[])

    def __repr__(self):
        return (
            f"<Profile(id={self.id}, urn={self.urn}, "
            f"name={self.name})>"
        )
