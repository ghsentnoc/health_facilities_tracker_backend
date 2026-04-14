from abc import ABC, abstractmethod
from typing import Any, Generic, Optional, TypeVar, Union

from fastapi import HTTPException, Request, status
from pydantic import BaseModel

from app.core.custom_exceptions import EntityDoesNotExistsError, ObjectAlreadyExistsException
from app.core.repositories.sql_base_repository import BaseReadRepository, BaseRepository, BaseWriteRepository
from app.core.schemas.query_params_schemas import AllowedFilterSchema, AllowedSortSchema
from app.core.utils.general import next_page, pagination_processor, previous_page, process_filter_sort_and_pagination
from app.core.utils.messages import ErrorMessages

T = TypeVar("T")


class BaseService(ABC, Generic[T]):
    """Base service class providing common functionality for all services."""

    def __init__(  # type: ignore
        self, *, main_repository: Union[BaseRepository, BaseReadRepository, BaseWriteRepository], **kwargs
    ) -> None:
        """The initializer for the base service.

        Args:
            main_repository (BaseRepository): The base repository to be making queries.
            kwargs: Any other repository needed for the service.
        """
        self.main_repository = main_repository

    def check_if_exists_deleted_or_not(self, *, field_name: str, value: Any) -> bool:
        """Check if an entity exists and if it is deleted or not.

        Args:
            field_name (str): The name of the field.
            value (Any): The value to filter by.

        Returns:
            bool: True if exists and deleted or not deleted, False if does not exist.
        """
        entity = (
            self.main_repository.db_session.query(self.main_repository.model).filter_by(**{field_name: value}).first()
        )  # type: ignore

        return True if entity else False

    def check_if_exists_and_not_deleted(self, *, field_name: str, value: Any, operator: str = "eq") -> bool:
        """Check if an entity exists and is not deleted.

        Args:
            field_name (str): The name of the field.
            value (Any): The value to filter by.
            operator (str): The operator to filter by.

        Returns:
            bool: True if exists and not deleted, False if exists and deleted

        Raises:
            HTTPException: If the entity does not exist.
        """
        try:
            entity = self.main_repository.exist_but_deleted(field_name=field_name, value=value, operator=operator)  # type: ignore
        except EntityDoesNotExistsError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e

        return True if not entity else False

    def get_by_id(self, *, entity_id: str) -> T:
        """Get an entity by its ID.

        Args:
            entity_id (str): The id of the entity to get.

        Returns:
            T: The retrieved entity.

        Raises:
            HTTPException: If the entity does not exist.
        """
        # check if exist
        if not self.check_if_exists_and_not_deleted(field_name="id", value=entity_id, operator="eq"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorMessages.entity_does_not_exists(entity_type=self.main_repository.model, value=entity_id),
            )

        return self.main_repository.get_by_id(entity_id=entity_id)  # type: ignore

    def get_multiple_by_ids(self, *, ids: list[str]) -> list[T]:
        """Get multiple entities by their IDs.

        Args:
            ids (list[str]): The list of entity IDs to get.

        Returns:
            list[T]: A list of the retrieved entities.
        """
        return self.main_repository.get_multiple_by_ids(entity_ids=ids)  # type: ignore

    def get_by_field(self, *, field_name: str, value: Any, operator: str = "eq") -> Union[T, list[T]]:
        """Get entities by a specific field.

        Args:
            field_name (str): The name of the field.
            value (Any): The value to filter by.
            operator (str): The operator to filter by.

        Returns:
            Union[T, list[T]]: A list of entity instances matching the criteria.
        """
        entity = self.main_repository.get_by_field(field_name=field_name, value=value, operator=operator)  # type: ignore

        if entity is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorMessages.entity_does_not_exists(entity_type=self.main_repository.model, value=value),
            )

        return entity

    def delete(self, *, entity_id: str) -> T:
        """Delete an entity.

        Args:
            entity_id (str): The id of the entity to delete.

        Returns:
            T: The deleted entity.
        """
        return self._default_delete(entity_id=entity_id)

    def restore(self, *, entity_id: str) -> T:
        """Restore a deleted entity.

        Args:
            entity_id (str): The id of the entity to restore.

        Returns:
            T: The restored entity.

        Raises:
            HTTPException: If the entity does not exist.
        """
        return self._default_restore(entity_id=entity_id)

    def get_total_pages(self, pagination: Optional[str]) -> int:
        """Get the total number of pages.

        Args:
            pagination (str): The pagination query parameter

        Returns:
            int: The total number of pages.
        """
        processed_pagination = pagination_processor(pagination=pagination)

        if processed_pagination == {}:
            return 1
        else:
            return self.main_repository.get_total_pages(page_size=processed_pagination["page_size"])  # type: ignore

    def get_pagination_extras(self, request: Request) -> dict:
        """Get extra information for response.

        Returns:
            dict: The extra information.
        """
        extras: dict = {}

        pagination = request.query_params.get("pagination") if request.query_params.get("pagination") else None

        total_pages = self.get_total_pages(pagination=pagination)
        processed_pagination = pagination_processor(pagination=pagination)

        extras["total_records"] = self.get_total_number()
        extras["total_pages"] = total_pages
        extras["next_page"] = (
            next_page(page=processed_pagination["page"], total_pages=total_pages) if pagination else None
        )
        extras["previous_page"] = previous_page(page=processed_pagination["page"]) if pagination else None
        extras["current_page"] = processed_pagination["page"] if pagination else 1

        return extras

    def get_total_number(self) -> int:
        """Get the total number of records.

        Returns:
            int: The total number of records
        """
        return self.main_repository.get_total_count()  # type: ignore

    def _default_create(
        self,
        *,
        entity_schema: BaseModel,
        unique_field_to_check: Optional[Union[str, list[str]]] = None,
        unique_field_value: Optional[Union[str, dict[str, Union[str, None]]]] = None,
    ) -> T:
        """Default create entity method.

        Args:
            entity_schema (BaseModel): The schema for creating the entity.
            unique_field_to_check (str): The unique field to check before creating.
            unique_field_value (str): The unique value to check.

        Returns:
            T: The created entity.

        Raises:
            HTTPException: If the entity already exists.
        """
        # check if an entity with unique field value exists
        entity = None

        # check for single unique field
        if unique_field_value and unique_field_to_check:
            # check for single unique field
            if isinstance(unique_field_value, str) and isinstance(unique_field_to_check, str):
                try:
                    entity = self.main_repository.exist_but_deleted(  # type: ignore
                        field_name=unique_field_to_check, value=unique_field_value, operator="eq"
                    )
                except EntityDoesNotExistsError:
                    pass

            # check for multiple unique fields
            if isinstance(unique_field_value, dict) and isinstance(unique_field_to_check, list):
                # check for each unique field
                for field in unique_field_to_check:
                    try:
                        entity = self.main_repository.exist_but_deleted(  # type: ignore
                            field_name=field, value=unique_field_value[field], operator="eq"
                        )
                    except EntityDoesNotExistsError:
                        continue

        if entity or entity is False:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=ErrorMessages.already_exists(object_type=self.main_repository.model),
            )

        try:
            return self.main_repository.create(data=entity_schema.model_dump())  # type: ignore
        except ObjectAlreadyExistsException as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=ErrorMessages.already_exists(object_type=self.main_repository.model),
            ) from e

    def _default_get_all(
        self,
        *,
        filters_without_joins: list[str],
        filters_with_joins: Optional[list] = None,
        allowed_filters: list[AllowedFilterSchema],
        allowed_sorts: list[AllowedSortSchema],
        pagination: Optional[str] = None,
        filters: Optional[str] = None,
        sort: Optional[str] = None,
        jurisdiction_zone: Optional[list[str]] = None,
    ) -> list[T]:
        """Get all entities.

        Args:
            filters_with_joins (list): Filters with joins
            filters_without_joins (list): Filters without no joins
            allowed_filters (list[AllowedFilterSchema]): The list of allowed filters.
            allowed_sorts (list[AllowedSortSchema]): The list of allowed sorts.
            pagination (dict[str, int]): Pagination parameters.
            filters (dict[str, Any]): Filter parameters.
            sort (dict[str, str]): Sort parameters.
            jurisdiction_zone (list[str], optional): Jurisdiction zone filters.

        Returns:
            list[T]: A list of all entity instances.
        """
        _filters, _sort, _pagination = process_filter_sort_and_pagination(
            filters=filters,
            sort=sort,
            pagination=pagination,
            allowed_filters=allowed_filters,
            allowed_sorts=allowed_sorts,
        )

        return self.main_repository.get_all(  # type: ignore
            filters_without_joins=filters_without_joins,
            pagination=_pagination,
            filters=_filters,
            sort=_sort,
            filters_with_joins=filters_with_joins,
        )

    def _default_delete(self, *, entity_id: str) -> T:
        """Delete an entity.

        Args:
            entity_id (str): The id of the entity to delete.

        Returns:
            T: The deleted entity.
        """
        entity = self.main_repository.get_by_id(entity_id=entity_id)  # type: ignore

        # check if the entity exists and is not deleted.
        if not self.check_if_exists_and_not_deleted(field_name="id", value=entity_id, operator="eq"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorMessages.entity_does_not_exists(entity_type=self.main_repository.model, value=entity_id),
            )

        return self.main_repository.delete(entity_to_delete=entity)  # type: ignore

    def _default_restore(self, *, entity_id: str) -> T:
        """Restore a deleted entity.

        Args:
            entity_id (str): The id of the entity to restore.

        Returns:
            T: The restored entity.

        Raises:
            HTTPException: If the entity does not exist.
        """
        entity_to_restore = self.main_repository.get_by_id(entity_id=entity_id)  # type: ignore

        # check if an entity exists is not deleted
        if self.check_if_exists_and_not_deleted(field_name="id", value=entity_id, operator="eq"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorMessages.cannot_restore_existing_entity(
                    entity_type=self.main_repository.model, value=entity_id
                ),
            )

        return self.main_repository.restore(entity_to_restore=entity_to_restore)  # type: ignore

    @abstractmethod
    def get_all(self, *args, **kwargs) -> list[T]:  # type: ignore
        """Get all entities."""

    @abstractmethod
    def create(self, *args, **kwargs) -> T:  # type: ignore
        """Create a new entity."""

    @abstractmethod
    def update(self, *args, **kwargs) -> T:  # type: ignore
        """Update an existing entity."""
