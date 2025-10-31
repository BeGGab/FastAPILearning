from typing import List, Any, Dict
import uuid
from typing import Union
from sqlalchemy import select, update, delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession


class BaseDAO:
    model = None

    @classmethod
    async def find_one_or_none_by_id(cls, session: AsyncSession, id: Union[uuid.UUID]):
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
            try:
                new_instance = cls.model(**values) # type: ignore
                session.add(new_instance)
                await session.commit()
                await session.refresh(new_instance)
                return new_instance
            except SQLAlchemyError as e:
                await session.rollback()
                raise e

    @classmethod
    async def add_many(cls, session: AsyncSession, values: List[Dict[str, Any]]):
        try:
            new_instances = [cls.model(**value) for value in values] # type: ignore
            session.add_all(new_instances)
            await session.commit()
            return new_instances
        except SQLAlchemyError as e:
            await session.rollback()
            raise e

    @classmethod
    async def update(cls, session: AsyncSession, id: int, **values):
        try:
            query = (
                update(cls.model)
                .where(cls.model.id == id)
                .values(**values)
                .execution_options(synchronize_session="fetch")
            )
            result = await session.execute(query)
            await session.commit()
            return result.rowcount
        except SQLAlchemyError as e:
            await session.rollback()
            raise e

    @classmethod
    async def delete(cls, session: AsyncSession, delete_all: bool = False, **filter_by):
        try:
            if delete_all:
                query = delete(cls.model)
            else:
                if not filter_by:
                    raise ValueError("Для удаления необходимо указать хотя бы один параметр фильтрации.")
                query = delete(cls.model).filter_by(**filter_by)

            result = await session.execute(query)
            await session.commit()
            return result.rowcount
        except SQLAlchemyError as e:
            await session.rollback()
            raise e
            
