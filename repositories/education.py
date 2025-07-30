from sqlalchemy.orm import Session
from typing import List

from abstractions.repository import IRepository
from models.education import Education


class EducationRepository(IRepository):
    """
    Repository class for managing Education entities in the database.
    Provides methods to create, retrieve, and list education records.
    """

    def __init__(self, session: Session):
        """
        Initialize the repository with a SQLAlchemy session.
        Args:
            session (Session): SQLAlchemy session object.
        """
        self.session = session
        self.model = Education

    def create(self, education: Education):
        """
        Add a new Education record to the database and commit the transaction.
        Args:
            education (Education): The Education object to add.
        """
        self.session.add(education)

    def get_by_urn(self, urn: str) -> Education:
        """
        Retrieve an Education record by its URN.
        Args:
            urn (str): The URN of the Education record.
        Returns:
            Education: The Education record if found, else None.
        """
        result = self.session.query(
            self.model
        ).filter(
            self.model.urn == urn
        ).first()
        return result

    def get_by_profile_id(self, profile_id: int) -> List[Education]:
        """
        Retrieve all Education records associated with a given profile ID.
        Args:
            profile_id (int): The profile ID to filter by.
        Returns:
            List[Education]: List of Education records for the profile.
        """
        results = self.session.query(
            self.model
        ).filter(
            self.model.profile_id == profile_id
        ).all()
        return results

    def get_by_id(self, id: int) -> Education:
        """
        Retrieve an Education record by its primary key ID.
        Args:
            id (int): The ID of the Education record.
        Returns:
            Education: The Education record if found, else None.
        """
        result = self.session.query(
            self.model
        ).filter(
            self.model.id == id
        ).first()
        return result

    def get_all(self) -> List[Education]:
        """
        Retrieve all Education records from the database.
        Returns:
            List[Education]: List of all Education records.
        """
        results = self.session.query(self.model).all()
        return results
