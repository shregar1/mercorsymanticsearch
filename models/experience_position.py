from sqlalchemy import (
    Column, String, Integer, Float, ForeignKey, Text
)

from models import Base
from models.experience import Experience


class ExperiencePosition(Base):

    __tablename__ = "experience_position"

    id = Column(Integer, primary_key=True, autoincrement=True)
    urn = Column(String, nullable=False)
    experience_id = Column(Integer, ForeignKey(Experience.id))
    title = Column(String)
    startDate = Column(String)
    endDate = Column(String)
    description = Column(Text)
    yearsOfWorkExperience = Column(Float)

    def __repr__(self):
        return (
            f"<ExperiencePosition(id={self.id}, title={self.title}, "
            f"experience_id={self.experience_id})>"
        )
