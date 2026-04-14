import json
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, status

from app.auth.models import RefreshToken
from app.auth.repositories.refresh_token_repository import RefreshTokenRepository
from app.auth.schemas.request.refresh_token import CreateRefreshTokenSchema, UpdateRefreshTokenSchema
from app.auth.utils.allowed_filters_sort import (
    allowed_refresh_token_filters,
    allowed_refresh_token_sorts,
    refresh_token_filters_without_joins,
)
from app.core.custom_exceptions import ObjectAlreadyExistsException
from app.core.services.base_service import BaseService


class RefreshTokenService(BaseService[RefreshToken]):
    """The service class for 'refresh_token'."""

    def __init__(self, *, refresh_token_repository: RefreshTokenRepository) -> None:
        """Initializer for 'refresh_token' service.

        Args:
            refresh_token_repository (RefreshTokenRepository): The refresh_token repository.
        """
        self.refresh_token_repository = refresh_token_repository
        super().__init__(main_repository=refresh_token_repository)

    def get_all(
        self, *, pagination: Optional[str] = None, filters: Optional[str] = None, sort: Optional[str] = None
    ) -> list[RefreshToken]:
        """Get all refresh_token entities.

        Args:
            pagination (dict[str, int]): Pagination parameters.
            filters (dict[str, Any]): Filter parameters.
            sort (dict[str, str]): Sort parameters.

        Returns:
            list[RefreshToken]: A list of all entity instances
        """
        return self._default_get_all(
            filters_without_joins=refresh_token_filters_without_joins,
            pagination=pagination,
            filters=filters,
            sort=sort,
            allowed_filters=allowed_refresh_token_filters,
            allowed_sorts=allowed_refresh_token_sorts,
        )

    def create(self, *, refresh_token_data: CreateRefreshTokenSchema) -> RefreshToken:
        """Create a new refresh_token.

        Args:
            refresh_token_data (CreateRefreshTokenSchema): The refresh_token data to create.

        Returns:
            RefreshToken: The newly created refresh_token.
        """
        return self._default_create(entity_schema=refresh_token_data)

    def update(self, *, refresh_token_id: str, data_to_update: UpdateRefreshTokenSchema) -> RefreshToken:
        """Update a refresh_token.

        Args:
            refresh_token_id (str): The ID of the refresh_token to update.
            data_to_update (UpdateRefreshTokenSchema): The data to update the refresh_token with.

        Returns:
            RefreshToken: The updated refresh_token.
        """
        refresh_token = self.get_by_id(entity_id=refresh_token_id)

        try:
            updated_refresh_token = self.refresh_token_repository.update(
                entity=refresh_token, update_data=data_to_update.model_dump()
            )
        except ObjectAlreadyExistsException as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e

        return updated_refresh_token

    def revoke_refresh_tokens(
        self,
        *,
        user_id: str,
        reason: str,
        new_token: Optional[str] = None,
    ) -> None:
        """Revoke all refresh tokens for a user.

        Args:
            user_id (str): The user ID.
            new_token (str): The new refresh token that replaced the old ones.
            reason (str): The reason for revocation.
        """
        refresh_tokens = self.get_all(filters=json.dumps({"user_id": {"value": user_id}, "revoked": {"value": False}}))

        for token in refresh_tokens:
            token_update_data = UpdateRefreshTokenSchema(
                revoked=True,
                revoked_at=datetime.now(tz=timezone.utc),
                replaced_by_token=new_token,
                revoked_reason=reason,
            )
            self.update(refresh_token_id=str(token.id), data_to_update=token_update_data)
