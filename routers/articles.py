import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse

from schemas.article import ArticleCreate, ArticleRead, ArticleUpdate
from services.articles import ArticleService, get_article_service
from services.pdf_generator import generate_simple_report

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/articles", tags=["Articles"])


@router.get(
    path="/",
    response_model=list[ArticleRead],
    tags=["Articles"],
)
async def get_articles(article_service: ArticleService = Depends(get_article_service)):
    try:
        return await article_service.get_all()
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to get articles")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get articles",
        ) from exc


@router.get(
    path="/report/pdf",
    summary="Download PDF report of all articles",
    tags=["Articles"],
)
async def get_articles_report(
    article_service: ArticleService = Depends(get_article_service),
):
    try:
        # 1. Отримуємо всі статті з бази даних
        articles = await article_service.get_all()

        # 2. Формуємо рядки для PDF
        content_lines = []
        for article in articles:
            # Використовуємо латиницю, щоб уникнути проблем зі шрифтами
            line = f"ID: {article.id} | Title: {article.title} | Author ID: {article.author_id}"
            content_lines.append(line)

        if not content_lines:
            content_lines.append("No articles found in the database.")

        # 3. Генеруємо PDF файл
        filepath = generate_simple_report(
            filename="articles_report.pdf",
            report_title="Database Report: Articles",
            content_lines=content_lines,
        )

        # 4. Повертаємо файл клієнту
        return FileResponse(
            path=filepath, filename="articles_report.pdf", media_type="application/pdf"
        )
    except Exception as exc:
        logger.exception("Failed to generate PDF report")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate report",
        ) from exc


@router.get(
    path="/{article_id}",
    response_model=ArticleRead,
    tags=["Articles"],
)
async def get_article(
    article_id: int, article_service: ArticleService = Depends(get_article_service)
):
    try:
        article = await article_service.get_by_id(article_id=article_id)
        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Article not found"
            )
        return article
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to get article with id %d", article_id)
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
async def create_article(
    article_data: ArticleCreate,
    article_service: ArticleService = Depends(get_article_service),
):
    try:
        return await article_service.create(data=article_data)
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
    article_service: ArticleService = Depends(get_article_service),
):
    try:
        article = await article_service.update(
            article_id=article_id, data=article_update
        )
        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Article not found"
            )
        return article
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to update article with id %s", article_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update article",
        ) from exc


@router.delete(
    path="/{article_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Articles"],
)
async def delete_article(
    article_id: int, article_service: ArticleService = Depends(get_article_service)
):
    try:
        deleted = await article_service.delete(article_id=article_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Article not found"
            )
        return None
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to delete article with id %s", article_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete article",
        ) from exc
