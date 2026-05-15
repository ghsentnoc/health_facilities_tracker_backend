from app.auth.models import APIKey, Application, AuthSession, Permission, RefreshToken, Role
from app.locations.models import District, Facility, Region
from app.users.models import User, UserFacilityAssociation, UserProfile

MODEL_MAP = {
    "district": District,
    "facility": Facility,
    "region": Region,
    "user": User,
    "role": Role,
    "permission": Permission,
    "user_profile": UserProfile,
    "user_facility_association": UserFacilityAssociation,
    "api_key": APIKey,
    "auth_session": AuthSession,
    "refresh_token": RefreshToken,
    "application": Application,
}
