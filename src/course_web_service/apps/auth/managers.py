import logging

from fastapi import Depends, HTTPException, status
from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError

from course_web_service.apps.auth.schemas import CreateUser, GetUserByEmail, UserInDB, UserReturnData
from course_web_service.core.core_dependecy.db_dependency import DBDependency
from course_web_service.database.models.user import User

logger = logging.getLogger(__name__)


class UserManager:
    def __init__(self, model: type[User] = User, db: DBDependency = Depends(DBDependency)) -> None:
        self.db = db
        self.model = model

    async def create_user(self, user: CreateUser) -> UserReturnData:
        logger.info(f"Starting writing new user to DB: {user.email}")
        async with self.db.db_session() as session:
            query = insert(self.model).values(**user.model_dump()).returning(self.model)

            try:
                result = await session.execute(query)
                await session.commit()
            except IntegrityError:
                logger.error(f"User already exists: {user.email}")
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User alredy exists.") from None

            user_data = result.scalars().first()
            logger.info(f"User {user.email} created successfully.")
            return UserReturnData(**user_data.__dict__)

    async def get_user_by_email(self, user: GetUserByEmail) -> UserInDB:
        async with self.db.db_session() as session:
            query = select(self.model).filter(self.model.email == user.email)

            try:
                result = await session.execute(query)
            except Exception as e:
                logger.error(f"Error fetching user by email: {e}")
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e) from None

            user_data = result.scalars().first()

            if not user_data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found.",
                )

            return UserInDB(**user_data.__dict__)
