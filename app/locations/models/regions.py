from typing import Any

from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from app.core.mixins.base_model_mixin import (
    AuditCreateMixin,
    AuditUpdateMixin,
    IdentityMixin,
    SoftDeleteMixin,
)
from app.database.base import Base


class Region(Base, IdentityMixin, AuditCreateMixin, AuditUpdateMixin, SoftDeleteMixin):
    """SQLAlchemy model for the 'regions' table.

    Represents a geographical region in the database.

    Attributes:
        name (str): The unique name of the region.
        districts (relationship): One-to-many relationship with District model.
    """

    __tablename__ = "regions"

    name = Column(String(50), unique=True, nullable=False)

    # Relationships
    districts = relationship("District", back_populates="region")

    def to_dict(self) -> dict[str, Any]:
        """Convert the Region instance to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "is_deleted": self.is_deleted,
            "deleted_at": self.deleted_at if self.deleted_at else None,
        }
