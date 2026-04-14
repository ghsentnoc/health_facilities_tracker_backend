import redis

from app.core.config.project_config import project_config
from app.core.config.redis_config import redis_config
from app.core.utils.constants import ProjectPlatformConstants

# set up redis configuration
redis_port = None
redis_host = (
    redis_config.REDIS_HOST
    if project_config.PROJECT_PLATFORM == ProjectPlatformConstants.LOCAL.value
    else redis_config.REDIS_DOCKER_HOST
)

if project_config.PROJECT_PLATFORM == ProjectPlatformConstants.LOCAL.value:
    if project_config.PROJECT_ENV == "DEV":
        redis_port = redis_config.REDIS_PORT_DEV
    elif project_config.PROJECT_ENV == "TEST":
        redis_port = redis_config.REDIS_PORT_TEST
    elif project_config.PROJECT_ENV == "PROD":
        redis_port = redis_config.REDIS_PORT_PROD
else:
    redis_port = redis_config.REDIS_DOCKER_PORT

# create connection pool
connection_pool = redis.ConnectionPool(
    host=redis_host,
    port=redis_port,
    password=redis_config.REDIS_PASSWORD,
    decode_responses=True,
    max_connections=redis_config.MAX_CONNECTION_POOL_SIZE,
)

# create redis client
redis_client = redis.Redis(connection_pool=connection_pool)
