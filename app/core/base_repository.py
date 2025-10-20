from abc import abstractmethod
from typing import Any, Generic, Optional, Type, TypeVar, Union

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Query, Session

from app.core.custom_exceptions import (
    EntityDoesNotExistsError,
    FailedToSaveObjectException,
    ObjectAlreadyExistsException,
)
from app.core.utils.general import (
    apply_filters_with_joins,
    apply_filters_with_no_joins,
    apply_sort,
    map_operator_to_function,
    offset_calculator,
)
from app.core.utils.messages import ErrorMessages

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """Base repository."""

    def __init__(self, *, db_session: Session, model: Type[T]):
        self.db_session = db_session
        self.model = model


class BaseReadRepository(BaseRepository[T]):
    """Base read repository."""

    def get_by_id(self, *, entity_id: str) -> Optional[T]:
        """Get an entity by its ID.

        Args:
            entity_id (str): The ID of the entity.

        Returns:
            T: The entity instance.
        """
        return self.db_session.query(self.model).filter_by(id=entity_id).first()

    def get_total_count(self) -> int:
        """Get the total count of entities.

        Returns:
            int: The total count of entities.
        """
        return self.db_session.query(self.model).count()

    def get_total_pages(self, *, page_size: int) -> int:
        """Get the total number of pages.

        Args:
            page_size (int): The number of entities per page.

        Returns:
            int: The total number of pages.
        """
        # Calculate total pages
        total_count = self.get_total_count()
        return (total_count + page_size - 1) // page_size

    def _default_get_all(
        self,
        *,
        query: Query,
        filters_without_joins: list[str],
        filters_with_joins: Optional[list] = None,
        pagination: Optional[dict[str, int]] = None,
        filters: Optional[dict[str, Any]] = None,
        sort: Optional[dict[str, str]] = None,
    ) -> Union[list[T], list[Type[T]]]:
        """Get all entities.

        Args:
            query (Query): The query to work on.
            filters_without_joins (list): Filters without no joins
            filters_with_joins (list): Filters with joins
            pagination (dict[str, int]): Pagination parameters.
            filters (dict[str, Any]): Filter parameters.
            sort (dict[str, str]): Sort parameters.

        Returns:
            list[T]: A list of all entity instances.
        """
        # check if there are filters
        # apply the filter to the query
        if filters:
            # apply filters with joins
            query = apply_filters_with_no_joins(
                query=query, model=self.model, filters=filters, filters_without_joins=filters_without_joins
            )

            if filters_with_joins:
                query = apply_filters_with_joins(filters=filters, filters_with_joins=filters_with_joins, query=query)

        # check if there are any sorts
        # apply the sort
        if sort:
            query = apply_sort(query=query, sort_items=sort, model=self.model)

        # check if there are any pagination
        # apply the pagination
        if pagination:
            query = query.offset(offset_calculator(page=pagination["page"], page_size=pagination["page_size"])).limit(
                pagination["page_size"]
            )

        return query.all()

    def get_by_field(self, *, field_name: str, value: Any, operator: str = "eq") -> Union[T, list[T]]:
        """Get entities by a specific field.

        Args:
            field_name (str): The name of the field.
            value (Any): The value to filter by.
            operator (str): The operator to filter by.

        Returns:
            list[T]: A list of entity instances matching the criteria.
        """
        # check if model has an attribute as the field name
        if not hasattr(self.model, field_name):
            raise AttributeError(f"'{self.model.__name__}' has no attribute '{field_name}'")

        # set the field
        field = getattr(self.model, field_name)

        operator_func = map_operator_to_function(operator=operator)
        result = self.db_session.query(self.model).filter(operator_func(field, value)).all()  # type: ignore

        # Check if the field is a string column
        # if hasattr(field, "type") and hasattr(field.type, "python_type") and field.type.python_type is str:
        #     # Case-insensitive comparison for strings
        #     if field_name != "id":
        #         result = self.db_session.query(self.model).filter(field.ilike(f"%{value}%")).all()
        #         return result if len(result) > 1 else result[0]

        # Default equality for non-string fields
        # result = self.db_session.query(self.model).filter(field == value).all()  # type: ignore
        return result if len(result) > 1 else result[0]

    def exist_but_deleted(self, *, field_name: str, value: Any, operator: str = "eq") -> bool:  # type: ignore
        """Check if an entity is deleted or not.

        Args:
            field_name (str): The name of the field to check.
            value (Any): The value to filter by
            operator (str): The operator to check filter by.

        Returns:
            bool: True if it's deleted otherwise False.
        """
        entity = self.get_by_field(field_name=field_name, value=value, operator=operator)

        if not entity:
            raise EntityDoesNotExistsError(ErrorMessages.entity_does_not_exists(entity_type=self.model, value=value))

        if entity:  # type: ignore
            if isinstance(entity, list):
                return all([_entity.is_deleted for _entity in entity])  # type: ignore
            elif isinstance(entity, type(T)):  # type: ignore
                return entity.is_deleted  # type: ignore
        return False

    @abstractmethod
    def get_all(
        self,
        *,
        filters_without_joins: list[str],
        filters_with_joins: Optional[list] = None,
        pagination: Optional[dict[str, int]] = None,
        filters: Optional[dict[str, Any]] = None,
        sort: Optional[dict[str, str]] = None,
    ) -> Union[list[T], list[Type[T]]]:  # type: ignore
        """Get all entities."""


class BaseWriteRepository(BaseRepository[T]):
    """Base write repository."""

    def save(self, *, object_to_save: T) -> T:
        """Save the object to the database.

        Args:
            object_to_save (T): The object to save

        Returns:
            T: The saved object.

        Raises:
            ObjectAlreadyExistsException: When object already exists
            FailedToSaveObjectException: When object fails to save
        """
        try:
            self.db_session.add(instance=object_to_save)
            self.db_session.commit()
            self.db_session.refresh(instance=object_to_save)
            return object_to_save
        except IntegrityError as e:
            if "UNIQUE constraint failed" in str(e) or "Duplicate entry" in str(e):
                self.db_session.rollback()
                raise ObjectAlreadyExistsException(
                    ErrorMessages.already_exists(object_type=type(object_to_save))
                ) from e
            else:
                self.db_session.rollback()
                raise FailedToSaveObjectException(str(e)) from e
        except Exception as e:
            self.db_session.rollback()
            raise FailedToSaveObjectException(str(e)) from e

    def save_all(self, *, objects_to_save: list[T]) -> list[T]:
        """Save the objects to the database.

        Args:
            objects_to_save (T): The object to save

        Returns:
            list[T]: The saved object.

        Raises:
            ObjectAlreadyExistsException: When object already exists
            FailedToSaveObjectException: When object fails to save
        """
        try:
            self.db_session.add_all(objects_to_save)
            self.db_session.commit()

            # Refresh all objects to ensure they are fully loaded with database values
            for record in objects_to_save:
                self.db_session.refresh(record)

            return objects_to_save

        except IntegrityError as e:
            if "UNIQUE constraint failed" in str(e) or "Duplicate entry" in str(e):
                self.db_session.rollback()
                raise ObjectAlreadyExistsException(
                    ErrorMessages.already_exists(object_type=type(objects_to_save[0]))
                ) from e
            else:
                raise FailedToSaveObjectException(str(e)) from e
        except Exception as e:
            self.db_session.rollback()
            raise FailedToSaveObjectException(str(e)) from e

    def delete(self, *, entity_to_delete: T) -> T:
        """Method to delete an entity.

        Args:
            entity_to_delete (T): The entity to delete

        Returns:
            T: The entity deleted
        """
        updated_entity = entity_to_delete.soft_delete()  # type: ignore
        return self.save(object_to_save=updated_entity)

    def restore(self, *, entity_to_restore: T) -> T:
        """Method to restore an entity.

        Args:
            entity_to_restore (T): The entity to restore

        Returns:
            T: The entity restored
        """
        updated_entity = entity_to_restore.restore()  # type: ignore
        return self.save(object_to_save=updated_entity)

    def update(self, *, entity: T, update_data: dict) -> T:  # type: ignore
        """Method to update an existing entity.

        Args:
            entity (T): The entity to update.
            update_data (dict): The data to update the entity with.

        Returns:
            T: The updated entity.
        """
        for key, value in update_data.items():
            if hasattr(entity, key):
                setattr(entity, key, value)

        return self.save(object_to_save=entity)

    def _default_create(self, *, data: dict) -> T:
        """Create a new entity.

        Args:
            data (dict): The data used to create a new entity.

        Returns:
            T: The newly created entity.
        """
        new_entity = self.model(**data)

        return self.save(object_to_save=new_entity)

    @abstractmethod
    def create(self, *args, **kwargs) -> T:  # type: ignore
        """Create a new entity."""
