import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.article import Article
from schemas.article import ArticleCreate, ArticleRead, ArticleUpdate
from settings.db import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/articles", tags=["Articles"])

SessionDepend = Annotated[AsyncSession, Depends(get_db)]


@router.get(
    path="/",
    response_model=list[ArticleRead],
    tags=["Articles"],
)
async def get_articles(session: SessionDepend):
    try:
        result = await session.execute(select(Article))
        return result.scalars().all()
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to get articles")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get articles",
        ) from exc


@router.get(
    path="/{article_id}",
    response_model=ArticleRead,
    tags=["Articles"],
)
async def get_article(article_id: int, session: SessionDepend):
    try:
        result = await session.execute(select(Article).where(Article.id == article_id))
        article = result.scalars().first()

        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Article not found"
            )

        return article

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(msg="Failed to get article with id %d", args=article_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get article",
        ) from exc


@router.post(
    path="/",
    response_model=ArticleRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Articles"],
)
async def create_article(article_data: ArticleCreate, session: SessionDepend):
    try:
        new_article = Article(**article_data.model_dump())
        session.add(new_article)
        await session.commit()
        await session.refresh(new_article)
        return new_article

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to create article")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create article",
        ) from exc


@router.put(
    path="/{article_id}",
    response_model=ArticleRead,
    tags=["Articles"],
)
async def update_article(
    article_id: int,
    article_update: ArticleUpdate,
    session: SessionDepend,
):
    try:
        result = await session.execute(select(Article).where(Article.id == article_id))
        existing_article = result.scalars().first()

        if not existing_article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Article not found"
            )

        for field, value in article_update.model_dump(exclude_unset=True).items():
            setattr(existing_article, field, value)

        session.add(existing_article)
        await session.commit()
        await session.refresh(existing_article)
        return existing_article

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(msg="Failed to update article with id %d", args=article_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update article",
        ) from exc


@router.delete(
    path="/{article_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Articles"],
)
async def delete_article(article_id: int, session: SessionDepend):
    try:
        result = await session.execute(select(Article).where(Article.id == article_id))
        existing_article = result.scalars().first()

        if not existing_article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Article not found"
            )

        await session.delete(existing_article)
        await session.commit()
        return None

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(msg="Failed to delete article with id %d", args=article_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete article",
        ) from exc
