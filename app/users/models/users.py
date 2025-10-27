from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.core.mixins.base import AuditCreateMixin, AuditUpdateMixin, IdentityMixin, SoftDeleteMixin
from app.core.models.associations import user_roles  # noqa: F401
from app.database.base import Base


class User(Base, IdentityMixin, AuditCreateMixin, AuditUpdateMixin, SoftDeleteMixin):
    """SQLAlchemy model for the 'users' table."""

    __tablename__ = "users"

    email = Column(String(100), unique=True, index=True)
    password_hash = Column(String(128), nullable=False)
    first_time_login = Column(Boolean, default=True)
    token_version = Column(Integer, default=0)
    is_logout = Column(Boolean, default=True)
    last_login = Column(DateTime, nullable=True)
    is_verified = Column(Boolean, default=False)
    is_suspended = Column(Boolean, default=False)
    is_approved = Column(Boolean, default=False)

    profile = relationship("UserProfile", back_populates="user", uselist=False)
    roles = relationship("Role", secondary="user_roles", back_populates="users")

    def to_dict(self) -> dict:
        """Convert User model to dictionary."""
        return {
            "id": self.id,
            "email": self.email,
            "first_name": self.profile.first_name if self.profile.first_name else None,
            "last_name": self.profile.last_name if self.profile.last_name else None,
            "phone_number": self.profile.phone_number if self.profile.phone_number else None,
            "country": self.profile.country if self.profile.country else None,
            "facility_name": self.profile.facility.name if self.profile.facility.name else None,
            "first_time_login": self.first_time_login,
            "token_version": self.token_version,
            "is_logout": self.is_logout,
            "last_login": self.last_login if self.last_login else None,
            "is_verified": self.is_verified,
            "is_suspended": self.is_suspended,
            "is_approved": self.is_approved,
            "is_deleted": self.is_deleted,
            "deleted_at": self.deleted_at if self.deleted_at else None,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
