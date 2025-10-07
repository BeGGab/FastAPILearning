from typing import List, Any, Dict

from sqlalchemy import select, update, delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from src.db import get_async_session 



class BaseDAO:
    model = None

    @classmethod
    async def find_one_or_none_by_id(cls, session: AsyncSession, id: int):
        query = select(cls.model).filter_by(id=id)
        result = await session.execute(query)
        return result.scalar_one_or_none()
    
    @classmethod
    async def find_one_or_none(cls, session: AsyncSession, **filter_by):
        query = select(cls.model).filter_by(**filter_by)
        result = await session.execute(query)
        return result.scalar_one_or_none()
    
    @classmethod
    async def find_all(cls, session: AsyncSession, **filter_by) -> List[Any]:
        query = select(cls.model).filter_by(**filter_by)
        result = await session.execute(query)
        return result.scalars().all()
    
    @classmethod
    async def add(cls, session: AsyncSession, **values):
        async with session.begin():
            try:
                new_instance = cls.model(**values)
                session.add(new_instance)
                session.commit()
            except SQLAlchemyError as e:
                await session.rollback()
                raise e
            return new_instance
        
    @classmethod
    async def add_many(cls, session: AsyncSession, values: List[Dict[str, Any]]):
        async with session.begin():
            new_instances = [cls.model(**item) for item in values]
            session.add_all(new_instances)
            try:
                await session.commit()
            except SQLAlchemyError as e:
                await session.rollback()
                raise e
            return new_instances
        


        @classmethod
        async def update(cls, session: AsyncSession, id: int, **values):
            async with session.begin():
                try:
                    query = (
                        update(cls.model)
                        .where(*[getattr(cls.model.id == id, k) == v for k, v in values.items()])
                        .values(**values)
                        .execution_options(synchronize_session="fetch")
                    )
                    result = await session.execeute(query)
                    await session.commit
                except SQLAlchemyError as e:
                    await session.rollback()
                    raise e
                return result.rowcount
            

        @classmethod
        async def delete(cls, session: AsyncSession, delete_all: bool = False, **filter_by):
            if delete_all is False:
                if not filter_by:
                    raise ValueError("Необходимо указать хотя бы один параметр для удаления.")
                
                async with session.begin():
                    try:
                        query = delete(cls.model).filter_by(**filter_by)
                        result = await session.execute(query)
                        await session.commit()
                    except SQLAlchemyError as e:
                        await session.rollback()
                        raise e
                    return result.rowcount
            


