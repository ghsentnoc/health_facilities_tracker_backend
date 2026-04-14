from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.mixins.base_model_mixin import AuditCreateMixin, AuditUpdateMixin, IdentityMixin, SoftDeleteMixin
from app.database.base import Base


class AuthSession(Base, IdentityMixin, AuditCreateMixin, AuditUpdateMixin, SoftDeleteMixin):
    """SQLAlchemy model for the 'auth_sessions' table."""

    __tablename__ = "auth_sessions"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_version = Column(Integer, nullable=False, default=0)
    device_id = Column(String(50), nullable=False, index=True)
    client_type = Column(String(25), nullable=False)

    __table_args__ = (UniqueConstraint("user_id", "device_id", "client_type", name="unq_user_client_device"),)

    user = relationship("User", back_populates="auth_sessions")

    def to_dict(self) -> dict:
        """Convert AuthSession model to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "token_version": self.token_version,
            "device_id": self.device_id,
            "client_type": self.client_type,
            "is_deleted": self.is_deleted,
            "deleted_at": self.deleted_at if self.deleted_at else None,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
