from sqlalchemy import (
    Column, String, Integer, Float, ForeignKey
)

from models import Base
from models.profile import Profile


class Experience(Base):
    __tablename__ = "experience"

    id = Column(Integer, primary_key=True, autoincrement=True)
    urn = Column(String, nullable=False)
    profile_id = Column(Integer, ForeignKey(Profile.id))
    company = Column(String)
    yearsOfWorkExperience = Column(Float)
    prestige_score = Column(Float)

    def __repr__(self):
        return (
            f"<Experience(id={self.id}, urn={self.urn}, "
            f"profile_id={self.profile_id})>"
        )
