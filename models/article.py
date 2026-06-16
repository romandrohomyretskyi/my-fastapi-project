from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    published_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"))
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))

    author = relationship("Author", back_populates="articles")
    category = relationship("Category", back_populates="articles")
