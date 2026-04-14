from sqlalchemy import Column, ForeignKey, String, Table, UniqueConstraint

from app.database.base import Base

# --------------Association between Roles and Permissions---------------
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", String(36), ForeignKey("roles.id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True),
    Column(
        "permission_id",
        String(36),
        ForeignKey("permissions.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
    ),
)

# -------------Association between Users and Roles-----------------
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("role_id", String(36), ForeignKey("roles.id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True),
    Column("user_id", String(36), ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True),
    UniqueConstraint("user_id", "role_id", name="unq_user_role"),
)


# ----------------Association between Application and Permissions----------------
application_permissions = Table(
    "application_permissions",
    Base.metadata,
    Column(
        "application_id",
        String(36),
        ForeignKey("applications.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
    ),
    Column(
        "permission_id",
        String(36),
        ForeignKey("permissions.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
    ),
)
