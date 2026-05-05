from datetime import datetime, timezone
from typing import Any

from sqlalchemy import Column, DateTime, ForeignKey, String
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


class FormResponse(Base, IdentityMixin, AuditCreateMixin, AuditUpdateMixin, SoftDeleteMixin):
    """SQLAlchemy model for the 'form_responses' table."""

    __tablename__ = "form_responses"

    form_id = Column(
        String(36),
        ForeignKey("forms.id", ondelete="CASCADE"),
        nullable=False,
    )
    submitted_by = Column(
        String(36),
        ForeignKey("users.id", onupdate="CASCADE"),
        nullable=True,
    )
    answers = Column(JSON, nullable=False)
    submitted_at = Column(DateTime, nullable=False, default=lambda: datetime.now(tz=timezone.utc))

    # Relationships
    form = relationship("Form", back_populates="responses")
    submitter = relationship("User", foreign_keys=[submitted_by])

    def to_dict(self) -> dict[str, Any]:
        """Convert the FormResponse instance to a dictionary."""
        return {
            "id": self.id,
            "form_id": self.form_id,
            "submitted_by": self.submitted_by if self.submitted_by else None,
            "answers": self.answers,
            "submitted_at": self.submitted_at,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "is_deleted": self.is_deleted,
            "deleted_at": self.deleted_at if self.deleted_at else None,
        }
