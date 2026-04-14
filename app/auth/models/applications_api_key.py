from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.mixins.base_model_mixin import AuditCreateMixin, AuditUpdateMixin, IdentityMixin, SoftDeleteMixin
from app.database.base import Base


class Application(Base, IdentityMixin, AuditCreateMixin, AuditUpdateMixin, SoftDeleteMixin):
    """SQLAlchemy model for the 'applications' table."""

    __tablename__ = "applications"

    user_id = Column(String(36), ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    app_name = Column(String(100), nullable=False, unique=True)
    platform = Column(String(30), nullable=False)
    is_active = Column(Boolean, default=False)
    api_key = None

    permissions = relationship("Permission", secondary="application_permissions", back_populates="applications")
    api_keys = relationship("APIKey", back_populates="application")
    user = relationship("User", back_populates="applications")

    def to_dict(self) -> dict:
        """Convert ClientReason model to dictionary."""
        response = {
            "id": self.id,
            "app_name": self.app_name,
            "platform": self.platform,
            "user_id": self.user_id,
            "is_active": self.is_active,
            "is_deleted": self.is_deleted,
            "deleted_at": self.deleted_at if self.deleted_at else None,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

        if self.api_key:
            response.update({"api_key": self.api_key})

        return response


class APIKey(Base, IdentityMixin, AuditCreateMixin, AuditUpdateMixin, SoftDeleteMixin):
    """SQLAlchemy model for the 'api_keys' table."""

    __tablename__ = "api_keys"

    application_id = Column(
        String(36), ForeignKey("applications.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False, index=True
    )
    api_key_id = Column(String(36), nullable=False)
    api_key_hash = Column(String(100), nullable=False)
    revoked = Column(Boolean, default=False)
    revoked_at = Column(DateTime, nullable=True)
    replaced_by_api_key = Column(String(512), nullable=True)
    last_used_at = Column(DateTime, nullable=True)
    expired_at = Column(DateTime, nullable=True)
    revoked_reason = Column(String(255), nullable=True)

    __table_args__ = (UniqueConstraint("application_id", "api_key_id", name="unq_app_api_key"),)

    application = relationship("Application", back_populates="api_keys")

    def to_dict(self) -> dict:
        """Convert ClientReason model to dictionary."""
        return {
            "id": self.id,
            "application_id": self.application_id,
            "api_key_id": self.api_key_id,
            "api_key_hash": self.api_key_hash,
            "revoked": self.revoked,
            "revoked_at": self.revoked_at if self.revoked_at else None,
            "replaced_by_api_key": self.replaced_by_api_key if self.replaced_by_api_key else None,
            "revoked_reason": self.revoked_reason if self.revoked_reason else None,
            "last_used_at": self.last_used_at if self.last_used_at else None,
            "expired_at": self.expired_at if self.expired_at else None,
            "is_deleted": self.is_deleted,
            "deleted_at": self.deleted_at if self.deleted_at else None,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
