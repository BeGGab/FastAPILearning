from contextlib import contextmanager
from datetime import datetime
import sqlalchemy as sa
from typing import Annotated, List, AsyncGenerator
from sqlalchemy import func, Text, String, ARRAY
from sqlalchemy.orm import mapped_column
from sqlalchemy.ext.asyncio import AsyncSession, AsyncAttrs, async_sessionmaker, create_async_engine


from src.config import Settings

settings = Settings()

engine = create_async_engine(str(settings.postgres_url))

async_session_maker = async_sessionmaker(engine, class_=AsyncAttrs, expire_on_commit=False)


uniq_str_an = Annotated[str, mapped_column(unique=True), mapped_column(Text, nullable=False)]
array_or_none_an = Annotated[List[str] | None, mapped_column(ARRAY(String))]
created_at = Annotated[datetime, mapped_column(sa.DateTime())]
updated_at = Annotated[datetime, mapped_column(sa.DateTime())]

'''@contextmanager
async def get_session() ->AsyncSession: 
    async with async_session_maker() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()'''


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()





'''@contextmanager
async def get_session() -> Session:
    session: Session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()'''