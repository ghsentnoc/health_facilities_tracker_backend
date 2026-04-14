from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from app.core.mixins.base_model_mixin import AuditCreateMixin, AuditUpdateMixin, IdentityMixin, SoftDeleteMixin
from app.core.models.associations import role_permissions, user_roles  # noqa: F401
from app.database.base import Base


class Permission(Base, IdentityMixin, AuditCreateMixin):
    """This class represents the table permissions from the database"""

    __tablename__ = "permissions"

    name = Column(String(100), unique=True, nullable=False)

    # relationships
    roles = relationship("Role", secondary="role_permissions", back_populates="permissions")
    applications = relationship("Application", secondary="application_permissions", back_populates="permissions")

    def to_dict(self) -> dict:
        """Returns a dictionary representation of the permission object"""
        return {"id": self.id, "name": self.name, "created_at": self.created_at}


class Role(Base, IdentityMixin, AuditCreateMixin, AuditUpdateMixin, SoftDeleteMixin):
    """This class represents the table roles from the database"""

    __tablename__ = "roles"

    name = Column(String(100), unique=True, nullable=False)

    users = relationship("User", secondary="user_roles", back_populates="roles")
    permissions = relationship("Permission", secondary="role_permissions", back_populates="roles")

    def to_dict(self) -> dict:
        """Dynamically convert Role object to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "permissions": [permission.to_dict() for permission in self.permissions],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "is_deleted": self.is_deleted,
            "deleted_at": self.deleted_at if self.deleted_at else None,
        }
