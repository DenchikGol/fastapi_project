import logging

from fastapi.security import OAuth2PasswordBearer

logger = logging.getLogger(__name__)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")
