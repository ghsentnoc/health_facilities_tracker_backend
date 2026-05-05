from typing import Any

from sqlalchemy import Column, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from app.core.mixins.base_model_mixin import (
    AuditCreateMixin,
    AuditUpdateMixin,
    IdentityMixin,
    SoftDeleteMixin,
)
from app.database.base import Base


class Form(Base, IdentityMixin, AuditCreateMixin, AuditUpdateMixin, SoftDeleteMixin):
    """SQLAlchemy model for the 'forms' table."""

    __tablename__ = "forms"

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_by = Column(
        String(36),
        ForeignKey("users.id", onupdate="CASCADE"),
        nullable=True,
    )
    status = Column(String(20), nullable=False, default="draft")

    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    sections = relationship(
        "FormSection",
        back_populates="form",
        order_by="FormSection.order",
        primaryjoin="and_(Form.id == FormSection.form_id, FormSection.is_deleted == False)",
    )
    responses = relationship("FormResponse", back_populates="form")

    def to_dict(self) -> dict[str, Any]:
        """Convert the Form instance to a dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description if self.description else None,
            "created_by": self.created_by if self.created_by else None,
            "status": self.status,
            "sections": [section.to_dict() for section in self.sections],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "is_deleted": self.is_deleted,
            "deleted_at": self.deleted_at if self.deleted_at else None,
        }
