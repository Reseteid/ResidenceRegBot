from app.database.models import async_session
from app.database.models import User
from sqlalchemy import select, update, delete
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def check_login(login: str) -> bool:
    async with async_session() as session:
        result = await session.execute(select(User).where(User.login == login))
        user = result.scalar_one_or_none()
        return user is not None
    
async def check_email(email: str) -> bool:
    async with async_session() as session:
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        return user is not None
    
async def add_user(data: dict) -> bool:
    async with async_session() as session:
        new_user = User(tg_id=data["tg_id"], adress=data["adress"], email=data["email"], login=data["login"], fio=data["fio"], password=data["password"])
        session.add(new_user)
        await session.commit()
        return True
    
async def verify_credentials(data: dict) -> bool:
    async with async_session() as session:
        result = await session.execute(select(User).where(User.login == data["login"]))
        user = result.scalar_one_or_none()
        if user is None:
            return False  # Пользователь не найден
        verified = pwd_context.verify(data["password"], user.password)  # Проверяем пароль
        return verified
    
async def email_exists(email: str) -> bool:
    async with async_session() as session:
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        return user is not None
    
async def update_user_password_by_email(data: dict) -> None:
    async with async_session() as session:
        stmt = (
            update(User).
            where(User.email == data["recovery_password"]).
            values(password=data["password"])
        )
        await session.execute(stmt)
        await session.commit()
        return True