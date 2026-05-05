from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi_mail import ConnectionConfig, FastMail
from pydantic import SecretStr

from app.auth.custom_exceptions import AuthHTTPException
from app.auth.routes.api.v1.application_routes import application_router
from app.auth.routes.api.v1.auth_routes import auth_router
from app.auth.routes.api.v1.permission_routes import permission_router
from app.auth.routes.api.v1.role_routes import role_router
from app.core.config.mail_config import mail_config
from app.core.custom_exceptions import InvalidEmailError, InvalidPasswordError, InvalidPhoneNumberError
from app.core.handlers.exceptions import (
    authentication_http_exception_handler,
    authentication_invalid_email_handler,
    authentication_invalid_password_handler,
    authentication_invalid_phone_number_handler,
    http_exception_handler,
    validation_exception_handler,
    value_error_exception_handler,
)
from app.core.routes.root import root_api_router
from app.core.utils.constants import ApplicationConstants
from app.forms.routes.api.v1.form_response_routes import form_response_router
from app.forms.routes.api.v1.form_routes import form_router
from app.locations.routes.api.v1.district_routes import district_router
from app.locations.routes.api.v1.facility_routes import facility_router
from app.locations.routes.api.v1.region_routes import region_router
from app.users.routes.api.v1.user_facility_association_routes import user_facility_association_router
from app.users.routes.api.v1.user_profile_routes import user_profile_router
from app.users.routes.api.v1.user_routes import user_router

app = FastAPI(
    title=ApplicationConstants.APP_NAME.value,
    description=ApplicationConstants.DESCRIPTION.value,
    redirect_slashes=True,
    docs_url="/api/documentation",
    openapi_url="/api/openapi.json",
    redoc_url="/api/redoc",
)

app_v1 = FastAPI(
    title=ApplicationConstants.APP_NAME.value,
    description=ApplicationConstants.DESCRIPTION.value,
    redirect_slashes=True,
    docs_url="/documentation",
    openapi_url="/openapi.json",
    redoc_url="/redoc",
)

##################################################################################
#                                                                                #
#                             MAIL CONFIGURATIONS                                #
#                                                                                #
##################################################################################
config = ConnectionConfig(
    MAIL_SERVER=mail_config.MAIL_SERVER,
    MAIL_PORT=mail_config.MAIL_PORT,
    MAIL_USERNAME=mail_config.MAIL_USERNAME,
    MAIL_PASSWORD=SecretStr(mail_config.MAIL_PASSWORD),
    MAIL_SSL_TLS=False,
    MAIL_STARTTLS=True,
    MAIL_FROM=mail_config.MAIL_FROM,
    TEMPLATE_FOLDER=Path(__file__).parent / "templates",
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    MAIL_DEBUG=True,
)

# Create the FastMail instance
fast_mail = FastMail(config=config)

##################################################################################
#                                                                                #
#                     ADD YOUR MIDDLEWARES HERE                           #
#                                                                                #
##################################################################################


##################################################################################
#                                                                                #
#                     ADD YOUR EXCEPTION HANDLERS HERE                           #
#                                                                                #
##################################################################################
app_v1.add_exception_handler(HTTPException, http_exception_handler)  # type: ignore
app_v1.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore
app_v1.add_exception_handler(ValueError, value_error_exception_handler)  # type: ignore
app_v1.add_exception_handler(AuthHTTPException, authentication_http_exception_handler)  # type: ignore
app_v1.add_exception_handler(InvalidEmailError, authentication_invalid_email_handler)  # type: ignore
app_v1.add_exception_handler(InvalidPasswordError, authentication_invalid_password_handler)  # type: ignore
app_v1.add_exception_handler(InvalidPhoneNumberError, authentication_invalid_phone_number_handler)  # type: ignore

##################################################################################
#                                                                                #
#                            ADD YOUR ROUTERS HERE                               #
#                                                                                #
##################################################################################
app_v1.include_router(root_api_router)

# User routes
app_v1.include_router(user_router)
app_v1.include_router(user_profile_router)
app_v1.include_router(user_facility_association_router)

# Auth routes
app_v1.include_router(auth_router)
app_v1.include_router(role_router)
app_v1.include_router(permission_router)

# Application routes
app_v1.include_router(application_router)

# Location routes
app_v1.include_router(region_router)
app_v1.include_router(district_router)
app_v1.include_router(facility_router)

# Form routes
app_v1.include_router(form_router)
app_v1.include_router(form_response_router)


##################################################################################
#                                                                                #
#                            ADD APP MOUNTS HERE                               #
#                                                                                #
##################################################################################
app.mount(ApplicationConstants.API_V1_STR.value, app_v1)
