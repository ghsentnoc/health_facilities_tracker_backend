from typing import Any

from sqlalchemy import Boolean, Column, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.mixins.base_model_mixin import (
    AuditCreateMixin,
    AuditUpdateMixin,
    IdentityMixin,
    SoftDeleteMixin,
)
from app.database.base import Base

# from app.users.models import UserProfile  # noqa: F401


class Facility(Base, IdentityMixin, AuditCreateMixin, AuditUpdateMixin, SoftDeleteMixin):
    """SQLAlchemy model for the 'facilities' table."""

    __tablename__ = "facilities"

    name = Column(String(255), nullable=False)
    registration_number = Column(String(100), nullable=True)
    facility_type = Column(String(100), nullable=False)
    ownership = Column(String(100), nullable=False)
    district_id = Column(
        String(36),
        ForeignKey("districts.id", onupdate="CASCADE"),
        nullable=False,
    )
    ghana_post_address = Column(String(25), nullable=True)
    latitude = Column(Numeric(10, 8), nullable=True)
    longitude = Column(Numeric(12, 9), nullable=True)
    altitude = Column(Numeric(14, 9), nullable=True)
    is_approved = Column(Boolean, default=False)
    is_licensed = Column(Boolean, default=False)

    __table_args__ = (UniqueConstraint("district_id", "name", name="unq_district_facility"),)

    # Relationships
    district = relationship("District", back_populates="facilities")
    contact_numbers = relationship("FacilityContact", back_populates="facility")
    user_facility = relationship("UserFacilityAssociation", back_populates="facility")

    def to_dict(self) -> dict[str, Any]:
        """Convert the Facility instance to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "registration_number": self.registration_number if self.registration_number else None,
            "facility_type": self.facility_type,
            "ownership": self.ownership,
            "district_name": self.district.name,
            "district_id": self.district.id,
            "region_name": self.district.region.name,
            "region_id": self.district.region.id,
            "ghana_post_address": self.ghana_post_address if self.ghana_post_address else None,
            "longitude": self.longitude if self.longitude else None,
            "latitude": self.latitude if self.latitude else None,
            "altitude": self.altitude if self.altitude else None,
            "is_approved": self.is_approved,
            "is_licensed": self.is_licensed,
            "contact_numbers": [contact.contact_number for contact in self.contact_numbers],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "is_deleted": self.is_deleted,
            "deleted_at": self.deleted_at if self.deleted_at else None,
        }


class FacilityContact(Base, IdentityMixin, AuditCreateMixin, AuditUpdateMixin, SoftDeleteMixin):
    """SQLAlchemy model for the 'facility_contacts' table."""

    __tablename__ = "facility_contacts"

    facility_id = Column(String(36), ForeignKey("facilities.id", ondelete="CASCADE"), nullable=False)
    contact_number = Column(String(20), nullable=False)

    # Relationships
    facility = relationship("Facility", back_populates="contact_numbers")

    def to_dict(self) -> dict[str, Any]:
        """Convert the FacilityContact instance to a dictionary."""
        return {
            "id": self.id,
            "facility_id": self.facility_id,
            "facility_name": self.facility.name,
            "contact_number": self.contact_number,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "is_deleted": self.is_deleted,
            "deleted_at": self.deleted_at if self.deleted_at else None,
        }
