from sqlalchemy.orm import Session
from typing import List

from abstractions.repository import IRepository
from models.experience_position import ExperiencePosition


class ExperiencePositionRepository(IRepository):
    """
    Repository class for managing ExperiencePosition entities in the database.
    Provides methods to create, retrieve, and list experience position records.
    """

    def __init__(self, session: Session):
        """
        Initialize the repository with a SQLAlchemy session.
        Args:
            session (Session): SQLAlchemy session object.
        """
        self.session = session
        self.model = ExperiencePosition

    def create(self, position: ExperiencePosition):
        """
        Add a new ExperiencePosition record to the database
        and commit the transaction.
        Args:
            position (ExperiencePosition): The ExperiencePosition object
            to add.
        """
        self.session.add(position)

    def get_by_id(self, id: int) -> ExperiencePosition:
        """
        Retrieve an ExperiencePosition record by its primary key ID.
        Args:
            id (int): The ID of the ExperiencePosition record.
        Returns:
            ExperiencePosition: The ExperiencePosition record if found,
            else None.
        """
        result = self.session.query(
            self.model,
        ).filter(
            self.model.id == id,
        ).first()
        return result

    def get_by_experience_id(
        self,
        experience_id: int,
    ) -> List[ExperiencePosition]:
        """
        Retrieve all ExperiencePosition records associated with a
        given experience ID.
        Args:
            experience_id (int): The experience ID to filter by.
        Returns:
            List[ExperiencePosition]: List of ExperiencePosition records for
            the experience.
        """
        results = self.session.query(self.model).filter(
            self.model.experience_id == experience_id,
        ).all()
        return results

    def get_all(self) -> List[ExperiencePosition]:
        """
        Retrieve all ExperiencePosition records from the database.
        Returns:
            List[ExperiencePosition]: List of all ExperiencePosition records.
        """
        results = self.session.query(self.model).all()
        return results
