import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import Boolean, Column, DateTime, String


class IdentityMixin:
    """This is a mixin that allows you to create a new identity for an entity."""

    id = Column(
        String(length=36), nullable=False, primary_key=True, unique=True, index=True, default=lambda: str(uuid.uuid4())
    )

    def __str__(self) -> str:
        """String representation for the entity."""
        return f"<{self.__class__.__name__} {self.id}>"


class AuditCreateMixin:
    """This is a mixin that allows you to create a new audit for an entity."""

    created_at = Column(DateTime, nullable=False, default=datetime.now(tz=timezone.utc))


class AuditUpdateMixin:
    """This is a mixin that allows you to update an audit for an entity"""

    updated_at = Column(
        DateTime, nullable=False, onupdate=datetime.now(tz=timezone.utc), default=datetime.now(tz=timezone.utc)
    )


class SoftDeleteMixin:
    """This is a mixin that allows you to create a new soft delete for an entity."""

    is_deleted = Column(Boolean, nullable=True, default=False)
    deleted_at = Column(DateTime, nullable=True)

    def soft_delete(self) -> Any:
        """Delete an entity partially from the database."""
        self.is_deleted = True  # type: ignore
        self.deleted_at = datetime.now(tz=timezone.utc)  # type: ignore
        return self

    def restore(self) -> Any:
        """Restore a deleted entity in the database."""
        self.is_deleted = False  # type: ignore
        self.deleted_at = None  # type: ignore
        return self
