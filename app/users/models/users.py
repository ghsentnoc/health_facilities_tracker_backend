from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.core.mixins.base_model_mixin import AuditCreateMixin, AuditUpdateMixin, IdentityMixin, SoftDeleteMixin
from app.core.models.associations import user_roles  # noqa: F401
from app.database.base import Base


class User(Base, IdentityMixin, AuditCreateMixin, AuditUpdateMixin, SoftDeleteMixin):
    """SQLAlchemy model for the 'users' table."""

    __tablename__ = "users"

    email = Column(String(100), unique=True, index=True)
    password_hash = Column(String(128), nullable=True)
    first_time_login = Column(Boolean, default=True)
    token_version = Column(Integer, default=0)
    last_login = Column(DateTime, nullable=True)
    is_verified = Column(Boolean, default=False)
    is_suspended = Column(Boolean, default=False)
    is_approved = Column(Boolean, default=False)

    profile = relationship("UserProfile", back_populates="user", uselist=False)
    user_facility = relationship("UserFacilityAssociation", back_populates="user", uselist=False)
    roles = relationship("Role", secondary="user_roles", back_populates="users")
    refresh_tokens = relationship("RefreshToken", back_populates="user")
    applications = relationship("Application", back_populates="user")
    auth_sessions = relationship("AuthSession", back_populates="user")

    def to_dict(self) -> dict:
        """Convert User model to dictionary."""
        return {
            "id": self.id,
            "email": self.email,
            "profile": self.profile.to_dict(),
            "facility": (
                {
                    "id": self.user_facility.facility_id,
                    "name": self.user_facility.to_dict().get("facility_name"),
                }
                if self.user_facility
                else None
            ),
            "first_time_login": self.first_time_login,
            "token_version": self.token_version,
            "is_logout": getattr(self, "is_logout", False),
            "last_login": self.last_login if self.last_login else None,
            "is_verified": self.is_verified,
            "is_suspended": self.is_suspended,
            "is_approved": self.is_approved,
            "is_deleted": self.is_deleted,
            "deleted_at": self.deleted_at if self.deleted_at else None,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
