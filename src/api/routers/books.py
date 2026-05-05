"""Books router.

Endpoints preserve the existing HTTP contract while delegating behavior to
application use cases.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from api.dependencies import get_book_repo
from api.mappers import book_to_dict
from api.schemas import BookPayload
from application.use_cases.create_book import create_book
from application.use_cases.delete_book import delete_book
from application.use_cases.list_books import list_books
from application.use_cases.read_book import get_book
from application.use_cases.replace_book import replace_book
from application.use_cases.search_books import get_books_by_name
from domain.repositories import BookRepository

router = APIRouter()


@router.get("/books")
async def list_books_endpoint(
    repo: Annotated[BookRepository, Depends(get_book_repo)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    """List books with pagination.

    Args:
        repo: Repository port injected via dependency.
        limit: Maximum number of books to return (1-100, default 20).
        offset: Number of books to skip (default 0).
    """
    return [book_to_dict(b) for b in await list_books(repo, limit=limit, offset=offset)]


@router.get("/books/{book_id}")
async def get_book_endpoint(
    book_id: str, repo: Annotated[BookRepository, Depends(get_book_repo)]
):
    """Get a book by id."""
    book = await get_book(repo, book_id)
    if book is not None:
        return book_to_dict(book)
    raise HTTPException(status_code=404, detail="Not found")


@router.get("/books/by-name/{name}")
async def get_books_by_name_endpoint(
    name: str, repo: Annotated[BookRepository, Depends(get_book_repo)]
):
    """Search books by name (case-insensitive substring match)."""
    return [book_to_dict(b) for b in await get_books_by_name(repo, name)]


@router.post("/books")
async def create_book_endpoint(
    book: BookPayload, repo: Annotated[BookRepository, Depends(get_book_repo)]
):
    """Create a book."""
    created = await create_book(
        repo,
        name=book.name,
        author=book.author,
        description=book.description,
        url=book.url,
        content=book.content,
    )
    return book_to_dict(created)


@router.put("/books/{book_id}")
async def replace_book_endpoint(
    book_id: str,
    book: BookPayload,
    repo: Annotated[BookRepository, Depends(get_book_repo)],
):
    """Replace a book (PUT semantics)."""
    updated = await replace_book(
        repo,
        book_id,
        name=book.name,
        author=book.author,
        description=book.description,
        url=book.url,
        content=book.content,
    )
    if updated is not None:
        return book_to_dict(updated)
    raise HTTPException(status_code=404, detail="Not found")


@router.delete("/books/{book_id}")
async def delete_book_endpoint(
    book_id: str, repo: Annotated[BookRepository, Depends(get_book_repo)]
):
    """Delete a book."""
    existing = await get_book(repo, book_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Not found")

    deleted = await delete_book(repo, book_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Not found")
    return {"deleted": book_to_dict(existing)}
