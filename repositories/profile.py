from sqlalchemy.orm import Session
from typing import List

from abstractions.repository import IRepository
from models.profile import Profile


class ProfileRepository(IRepository):
    """
    Repository class for managing Profile entities in the database.
    Provides methods to create, retrieve, and list profile records.
    """

    def __init__(self, session: Session):
        """
        Initialize the repository with a SQLAlchemy session.
        Args:
            session (Session): SQLAlchemy session object.
        """
        self.session = session
        self.model = Profile

    def create(self, profile: Profile):
        """
        Add a new Profile record to the database and commit the transaction.
        Args:
            profile (Profile): The Profile object to add.
        """
        self.session.add(profile)

    def get_by_id(self, id: int) -> Profile:
        """
        Retrieve a Profile record by its primary key ID.
        Args:
            id (int): The ID of the Profile record.
        Returns:
            Profile: The Profile record if found, else None.
        """
        result = self.session.query(
            self.model,
        ).filter(
            self.model.id == id,
        ).first()
        return result

    def get_by_urn(self, urn: str) -> Profile:
        """
        Retrieve a Profile record by its URN.
        Args:
            urn (str): The URN of the Profile record.
        Returns:
            Profile: The Profile record if found, else None.
        """
        result = self.session.query(
            self.model,
        ).filter(
            self.model.urn == urn,
        ).first()
        return result

    def get_all(self) -> List[Profile]:
        """
        Retrieve all Profile records from the database.
        Returns:
            List[Profile]: List of all Profile records.
        """
        results = self.session.query(self.model).all()
        return results
