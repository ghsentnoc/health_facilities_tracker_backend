from sqlalchemy import Column, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.mixins.base_model_mixin import AuditCreateMixin, AuditUpdateMixin, IdentityMixin, SoftDeleteMixin
from app.database.base import Base
from app.locations.models import Facility  # noqa


class UserProfile(Base, IdentityMixin, AuditCreateMixin, AuditUpdateMixin, SoftDeleteMixin):
    """SQLAlchemy model for the 'user_profiles' table."""

    __tablename__ = "user_profiles"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    phone_number = Column(String(15), nullable=False, unique=True)
    country = Column(String(50), nullable=False)

    # Relationships
    user = relationship("User", back_populates="profile")

    @property
    def get_first_name(self) -> str:
        """Return the first name."""
        return str(self.first_name)

    @property
    def get_last_name(self) -> str:
        """Return the last name."""
        return str(self.last_name)

    @property
    def get_phone_number(self) -> str:
        """Return the phone number."""
        return str(self.phone_number)

    @property
    def get_country(self) -> str:
        """Return the country."""
        return str(self.country)

    def to_dict(self) -> dict:
        """Convert UserProfile model to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone_number": self.phone_number,
            "country": self.country,
            "is_deleted": self.is_deleted,
            "deleted_at": self.deleted_at if self.deleted_at else None,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class UserFacilityAssociation(Base, IdentityMixin, AuditCreateMixin, AuditUpdateMixin, SoftDeleteMixin):
    """SQLAlchemy model for the 'user_profiles_facilities' association table."""

    __tablename__ = "user_profiles_facilities"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    facility_id = Column(String(36), ForeignKey("facilities.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (
        # Ensure a user can only be associated with a facility once
        UniqueConstraint("user_id", "facility_id", name="uix_user_facility"),
        UniqueConstraint("user_id", name="uix_user"),  # Ensure a user can only have one profile
    )

    # Relationships
    user = relationship("User", back_populates="user_facility")
    facility = relationship("Facility", back_populates="user_facility")

    def to_dict(self) -> dict:
        """Convert UserFacilityAssociation model to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user.id,
            "facility_id": self.facility_id,
            "facility_name": self.facility.name,
            "is_deleted": self.is_deleted,
            "deleted_at": self.deleted_at if self.deleted_at else None,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
