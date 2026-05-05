from typing import Any

from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.mixins.base_model_mixin import (
    AuditCreateMixin,
    AuditUpdateMixin,
    IdentityMixin,
    SoftDeleteMixin,
)
from app.database.base import Base


class FormSection(Base, IdentityMixin, AuditCreateMixin, AuditUpdateMixin, SoftDeleteMixin):
    """SQLAlchemy model for the 'form_sections' table."""

    __tablename__ = "form_sections"

    form_id = Column(
        String(36),
        ForeignKey("forms.id", ondelete="CASCADE"),
        nullable=False,
    )
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    order = Column(Integer, nullable=False, default=0)

    # Relationships
    form = relationship("Form", back_populates="sections")
    fields = relationship(
        "FormField",
        back_populates="section",
        order_by="FormField.order",
        primaryjoin="and_(FormSection.id == FormField.section_id, FormField.is_deleted == False)",
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert the FormSection instance to a dictionary."""
        return {
            "id": self.id,
            "form_id": self.form_id,
            "title": self.title if self.title else None,
            "description": self.description if self.description else None,
            "order": self.order,
            "fields": [field.to_dict() for field in self.fields],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "is_deleted": self.is_deleted,
            "deleted_at": self.deleted_at if self.deleted_at else None,
        }
