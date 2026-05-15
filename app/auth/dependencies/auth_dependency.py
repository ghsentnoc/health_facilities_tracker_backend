import logging
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.auth.config.auth_config import auth_config
from app.auth.dependencies.api_keys_dependency import create_api_key_service
from app.auth.dependencies.auth_session_service_dependency import create_auth_session_service
from app.auth.dependencies.role_service_dependency import create_role_service
from app.auth.models import APIKey, Application
from app.auth.services.token_service import TokenService
from app.auth.utils.constants import TokenTypeConstants
from app.auth.utils.hash_password import PasswordHashManager
from app.core.custom_exceptions import ExpiredTokenError, InvalidTokenError
from app.core.dependencies.database_dependency import db_session_dependency
from app.core.utils.messages import ErrorMessages
from app.users.dependencies.user_service_dependency import create_user_service
from app.users.models import User

# Load environment variables from .env file
load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)

oauth2_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    *,
    token: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db_session: Session = Depends(db_session_dependency),
) -> User | None:
    """Get the current user from the token.

    Args:
        token (str): The token. Defaults Depends(oauth2_scheme).
        db_session (Session): The database session. Default Depends(get_db).

    Returns:
        User: The authenticated user.
    """
    user_service = create_user_service(db_session=db_session)
    role_service = create_role_service(db_session=db_session)
    auth_session_service = create_auth_session_service(db_session=db_session)
    token_service = TokenService(
        secret=auth_config.JWT_SECRET_KEY,
        algorithm=auth_config.JWT_ALGORITHM,
    )

    if not token or token == "undefined":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # decode token
    try:
        payload = token_service.decode_token(token=token.credentials)
    except (ExpiredTokenError, InvalidTokenError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

    # check if token is an access token
    if payload.get("token_type") != TokenTypeConstants.ACCESS_TOKEN.value:
        logger.warning(f"Invalid token type: {payload.get('token_type')}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # get the user
    user = user_service.get_by_id(entity_id=payload.get("sub"))

    if not user.is_verified:  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ErrorMessages.NOT_VERIFIED.value,
        )

    # check if user is approved
    if not user.is_approved:  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ErrorMessages.entity_not_approved(object_type=User, value=str(user.email)),
        )

    # check if user is suspended
    if user.is_suspended:  # type: ignore
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=ErrorMessages.ACCOUNT_SUSPENDED.value)

    # get the user active role
    if payload.get("active_role"):
        role = role_service.get_by_field(field_name="name", value=payload.get("active_role"), operator="eq")

        user.active_role = role  # type: ignore

    session_id = payload.get("session_id")
    session_token_version = payload.get("session_token_version")
    if not session_id or session_token_version is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        auth_session = auth_session_service.get_by_id(entity_id=session_id)
    except HTTPException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

    if auth_session.user_id != user.id or auth_session.is_deleted:  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if str(auth_session.token_version) != str(session_token_version):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # check if the token version is valid
    if user.token_version != payload["token_version"]:
        logger.warning(f"Token is not valid: {payload.get('sub')}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def validate_api_key(
    x_api_key: Annotated[str, Header()], db_session: Session = Depends(db_session_dependency)
) -> Application:
    """Validate an api key.

    Args:
        x_api_key (str): The api key to validate.
        db_session (Session): The database session.

    Returns:
        Application: The application the api key belongs to.
    """
    api_key_service = create_api_key_service(db_session=db_session)
    user_service = create_user_service(db_session=db_session)
    hash_manager = PasswordHashManager()

    # check if the api key exists.
    if not x_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing API key in header: x-api-key")

    try:
        # get api_key_id and secret_key from api key
        secret_key, api_key_id = x_api_key.split(".")
    except ValueError as e:
        logger.error("Invalid API key format.")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Malformed API key.") from e

    # retrieve api key from db
    api_key = api_key_service.get_by_field(field_name="api_key_id", value=api_key_id, operator="eq")

    # check if api key is deleted or not
    if api_key.is_deleted:  # type: ignore
        logger.warning("API key is deleted")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorMessages.entity_does_not_exists(entity_type=APIKey, value=x_api_key),  # type: ignore
        )

    # retrieve user from db
    user = user_service.get_by_id(entity_id=api_key.application.user_id)  # type: ignore

    # check if api key is revoked or not
    if api_key.revoked:  # type: ignore
        logger.warning("API key is revoked")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ErrorMessages.UNAUTHORIZED_APP.value)

    # check if the application exists
    if api_key.application.is_deleted:  # type: ignore
        logger.warning("API key application is deleted")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorMessages.entity_does_not_exists(entity_type=Application, value=x_api_key),
        )

    # check if the application is active
    if not api_key.application.is_active:  # type: ignore
        logger.warning("API key application is inactive")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ErrorMessages.INACTIVE_APPLICATION.value)

    # verify secret
    if not hash_manager.verify_password(plain_password=secret_key, hashed_password=str(api_key.api_key_hash)):  # type: ignore
        logger.warning("API key is not correct")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=ErrorMessages.UNAUTHENTICATED_APP.value)

    # check if user associated with application exists or suspended
    if user.is_deleted or user.is_suspended or not user.is_verified:
        logger.warning("API key user is deleted, suspended or not verified")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ErrorMessages.INACTIVE_APPLICATION.value)

    return api_key.application  # type: ignore
