from typing import Any

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.mixins.base_model_mixin import (
    AuditCreateMixin,
    AuditUpdateMixin,
    IdentityMixin,
    SoftDeleteMixin,
)
from app.database.base import Base

try:
    from sqlalchemy import JSON
except ImportError:
    from sqlalchemy import Text as JSON  # type: ignore


class FormField(Base, IdentityMixin, AuditCreateMixin, AuditUpdateMixin, SoftDeleteMixin):
    """SQLAlchemy model for the 'form_fields' table."""

    __tablename__ = "form_fields"

    section_id = Column(
        String(36),
        ForeignKey("form_sections.id", ondelete="CASCADE"),
        nullable=False,
    )
    form_id = Column(
        String(36),
        ForeignKey("forms.id", ondelete="CASCADE"),
        nullable=False,
    )
    label = Column(String(255), nullable=False)
    field_type = Column(String(50), nullable=False)
    required = Column(Boolean, nullable=False, default=False)
    placeholder = Column(String(255), nullable=True)
    options = Column(JSON, nullable=True)
    validation = Column(JSON, nullable=True)
    default_value = Column(String(255), nullable=True)
    order = Column(Integer, nullable=False, default=0)
    conditional_logic = Column(JSON, nullable=True)
    help_text = Column(String(500), nullable=True)

    # Relationships
    section = relationship("FormSection", back_populates="fields")
    form = relationship("Form", foreign_keys=[form_id])

    def to_dict(self) -> dict[str, Any]:
        """Convert the FormField instance to a dictionary."""
        return {
            "id": self.id,
            "section_id": self.section_id,
            "form_id": self.form_id,
            "label": self.label,
            "field_type": self.field_type,
            "required": self.required,
            "placeholder": self.placeholder if self.placeholder else None,
            "options": self.options if self.options else None,
            "validation": self.validation if self.validation else None,
            "default_value": self.default_value if self.default_value else None,
            "order": self.order,
            "conditional_logic": self.conditional_logic if self.conditional_logic else None,
            "help_text": self.help_text if self.help_text else None,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "is_deleted": self.is_deleted,
            "deleted_at": self.deleted_at if self.deleted_at else None,
        }
