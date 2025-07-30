from sqlalchemy import (
    Column, String, Integer, Float, ForeignKey
)

from models import Base
from models.profile import Profile


class Education(Base):

    __tablename__ = "education"

    id = Column(Integer, primary_key=True, autoincrement=True)
    urn = Column(String, nullable=False)
    profile_id = Column(Integer, ForeignKey(Profile.id))
    school = Column(String)
    degree = Column(String)
    fieldOfStudy = Column(String)
    startDate = Column(String)
    endDate = Column(String)
    prestige_score = Column(Float)
    subject = Column(String)

    def __repr__(self):
        return (
            f"<EducationDegree(id={self.id}, urn={self.urn}, "
            f"profile_id={self.profile_id})>"
        )
