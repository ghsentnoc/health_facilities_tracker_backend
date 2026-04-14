from typing import Any

from sqlalchemy import Column, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.mixins.base_model_mixin import (
    AuditCreateMixin,
    AuditUpdateMixin,
    IdentityMixin,
    SoftDeleteMixin,
)
from app.database.base import Base


class District(Base, IdentityMixin, AuditCreateMixin, AuditUpdateMixin, SoftDeleteMixin):
    """SQLAlchemy model for the 'districts' table."""

    __tablename__ = "districts"

    name = Column(String(100), nullable=False)
    region_id = Column(
        String(36),
        ForeignKey("regions.id", onupdate="CASCADE"),
        nullable=False,
    )

    __table_args__ = (UniqueConstraint("region_id", "name", name="unq_region_district"),)

    # Relationships
    region = relationship("Region", back_populates="districts")
    facilities = relationship("Facility", back_populates="district")

    def to_dict(self) -> dict[str, Any]:
        """Convert the District instance to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "region_id": self.region_id,
            "region_name": self.region.name,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "is_deleted": self.is_deleted,
            "deleted_at": self.deleted_at if self.deleted_at else None,
        }
