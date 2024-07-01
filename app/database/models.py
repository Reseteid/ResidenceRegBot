from sqlalchemy import BigInteger, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, create_async_engine, async_sessionmaker

engine = create_async_engine('sqlite+aiosqlite:///db.sqlite3')

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass

class User (Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)
    adress = mapped_column(String(300))
    email = mapped_column(String(100), unique=True)
    login = mapped_column(String(100), unique=True)
    fio = mapped_column(String(150))
    password = mapped_column(String(500))
    code = mapped_column(String(6))

async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)



