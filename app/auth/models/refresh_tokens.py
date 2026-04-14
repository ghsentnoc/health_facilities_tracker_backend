from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship

from app.core.mixins.base_model_mixin import AuditCreateMixin, AuditUpdateMixin, IdentityMixin, SoftDeleteMixin
from app.database.base import Base


class RefreshToken(Base, IdentityMixin, AuditCreateMixin, AuditUpdateMixin, SoftDeleteMixin):
    """SQLAlchemy model for the 'refresh_tokens' table."""

    __tablename__ = "refresh_tokens"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_id = Column(String(36), nullable=False, unique=True, index=True)
    token = Column(String(512), nullable=False, unique=True, index=True)
    revoked = Column(Boolean, default=False)
    revoked_at = Column(DateTime, nullable=True)
    replaced_by_token = Column(String(512), nullable=True)
    revoked_reason = Column(String(255), nullable=True)
    expires_at = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="refresh_tokens")

    def to_dict(self) -> dict:
        """Convert RefreshToken model to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "token": self.token,
            "revoked": self.revoked,
            "revoked_at": self.revoked_at if self.revoked_at else None,
            "replaced_by_token": self.replaced_by_token if self.replaced_by_token else None,
            "revoked_reason": self.revoked_reason if self.revoked_reason else None,
            "expires_at": self.expires_at,
            "is_deleted": self.is_deleted,
            "deleted_at": self.deleted_at if self.deleted_at else None,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
