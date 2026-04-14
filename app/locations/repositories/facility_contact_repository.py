from typing import Any, Optional, Type, Union

from sqlalchemy.orm import Session

from app.core.repositories.sql_base_repository import BaseReadRepository, BaseWriteRepository
from app.locations.models import FacilityContact


class FacilityContactRepository(BaseReadRepository[FacilityContact], BaseWriteRepository[FacilityContact]):
    """Repository for managing FacilityContact entities."""

    def __init__(self, *, db_session: Session, model: type[FacilityContact] = FacilityContact) -> None:
        """Initialize the FacilityContactRepository with a database session and model.

        Args:
            db_session (Session): The SQLAlchemy database session.
            model (FacilityContact): The FacilityContact model class.
        """
        self.db_session = db_session
        self.model = model
        super().__init__(db_session=db_session, model=model)

    def create(self, *, data: dict[str, Any]) -> FacilityContact:
        """Create a new facility contact entity.

        Args:
            data (dict[str, Any]): The facility contact data needed to create the entity.

        Returns:
            FacilityContact: The newly created facility contact.
        """
        return self._default_create(data=data)

    def delete_by_facility_id(self, *, facility_id: str) -> list[FacilityContact]:
        """Delete facility contact entities by facility ID.

        Args:
            facility_id (str): The ID of the facility whose contacts are to be deleted.

        Returns:
            list[FacilityContact]: The deleted facility contact entities.
        """
        contacts_to_delete = (
            self.db_session.query(FacilityContact).filter(FacilityContact.facility_id == facility_id).all()
        )

        for contact in contacts_to_delete:
            self.delete(entity_to_delete=contact)

        return contacts_to_delete

    def delete_contact_number_for_facility(self, *, contact_number: str, facility_id: str) -> Optional[FacilityContact]:
        """Delete a specific contact number for a given facility ID.

        Args:
            contact_number (str): The contact number to be deleted.
            facility_id (str): The ID of the facility whose contact number is to be deleted.

        Returns:
            Optional[FacilityContact]: The deleted facility contact entity if found and deleted, None otherwise.
        """
        contact_to_delete = (
            self.db_session.query(FacilityContact)
            .filter(
                FacilityContact.contact_number == contact_number,
                FacilityContact.facility_id == facility_id,
            )
            .first()
        )

        if contact_to_delete:
            self.delete(entity_to_delete=contact_to_delete)

        return contact_to_delete

    def check_if_contact_already_exists_for_facility(self, *, contact_number: str, facility_id: str) -> bool:
        """Check if contact number already exist for the given facility ID.

        Args:
            contact_number (str): The contact number to check.
            facility_id (str): The ID of the facility.

        Returns:
            bool: True if any contact number already exists for the facility, False otherwise.
        """
        existing_contact = (
            self.db_session.query(FacilityContact)
            .filter(
                FacilityContact.contact_number == contact_number,
                FacilityContact.facility_id == facility_id,
            )
            .first()
        )

        return existing_contact is not None

    def get_all(
        self,
        *,
        filters_without_joins: list[str],
        filters_with_joins: Optional[list] = None,
        pagination: Optional[dict[str, int]] = None,
        filters: Optional[dict[str, Any]] = None,
        sort: Optional[dict[str, str]] = None,
    ) -> Union[list[FacilityContact], list[Type[FacilityContact]]]:
        """Get all facility contact entities."""
        # query = self.db_session.query(FacilityContact)
        # query = query.options(
        #     joinedload(FacilityContact.facility),
        # )

        # if filters:
        #     if filters.get("facility_name"):
        #         query = query.join(FacilityContact.facility)
        #         filters["facility_name"].update({"field_name": "name", "model": Facility})

        # return self._default_get_all(
        #     filters_without_joins=filters_without_joins,
        #     filters_with_joins=filters_with_joins,
        #     pagination=pagination,
        #     filters=filters,
        #     sort=sort,
        #     query=query,
        # )
        raise NotImplementedError
