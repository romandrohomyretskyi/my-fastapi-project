from typing import Sequence

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.article import Article
from schemas.article import ArticleCreate, ArticleUpdate
from settings.db import get_db


class ArticleService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> Sequence[Article]:
        result = await self.db.execute(select(Article))
        return result.scalars().all()

    async def get_by_id(self, article_id: int) -> Article | None:
        result = await self.db.execute(select(Article).where(Article.id == article_id))
        return result.scalars().first()

    async def create(self, data: ArticleCreate) -> Article:
        new_article = Article(**data.model_dump())
        self.db.add(new_article)
        await self.db.commit()
        await self.db.refresh(new_article)
        return new_article

    async def update(self, article_id: int, data: ArticleUpdate) -> Article | None:
        article = await self.get_by_id(article_id)
        if not article:
            return None

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(article, field, value)

        self.db.add(article)
        await self.db.commit()
        await self.db.refresh(article)
        return article

    async def delete(self, article_id: int) -> bool:
        article = await self.get_by_id(article_id)
        if not article:
            return False

        await self.db.delete(article)
        await self.db.commit()
        return True


async def get_article_service(db: AsyncSession = Depends(get_db)) -> ArticleService:
    return ArticleService(db)
