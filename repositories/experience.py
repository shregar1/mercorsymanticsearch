from sqlalchemy.orm import Session
from typing import List

from abstractions.repository import IRepository
from models.experience import Experience


class ExperienceRepository(IRepository):
    """
    Repository class for managing Experience entities in the database.
    Provides methods to create, retrieve, and list experience records.
    """

    def __init__(self, session: Session):
        """
        Initialize the repository with a SQLAlchemy session.
        Args:
            session (Session): SQLAlchemy session object.
        """
        self.session = session
        self.model = Experience

    def create(self, experience: Experience):
        """
        Add a new Experience record to the database and commit the transaction.
        Args:
            experience (Experience): The Experience object to add.
        """
        self.session.add(experience)

    def get_by_id(self, id: int) -> Experience:
        """
        Retrieve an Experience record by its primary key ID.
        Args:
            id (int): The ID of the Experience record.
        Returns:
            Experience: The Experience record if found, else None.
        """
        result = self.session.query(
            self.model,
        ).filter(
            self.model.id == id,
        ).first()
        return result

    def get_by_profile_id(self, profile_id: int) -> List[Experience]:
        """
        Retrieve all Experience records associated with a given profile ID.
        Args:
            profile_id (int): The profile ID to filter by.
        Returns:
            List[Experience]: List of Experience records for the profile.
        """
        results = self.session.query(
            self.model,
        ).filter(
            self.model.profile_id == profile_id,
        ).all()
        return results

    def get_all(self) -> List[Experience]:
        """
        Retrieve all Experience records from the database.
        Returns:
            List[Experience]: List of all Experience records.
        """
        results = self.session.query(self.model).all()
        return results
