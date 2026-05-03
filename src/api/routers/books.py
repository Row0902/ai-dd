"""Books router.

Endpoints preserve the existing HTTP contract while delegating behavior to
application use cases.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import get_book_repo
from api.mappers import book_to_dict
from api.schemas import BookPayload
from application.use_cases.book_use_case import (
    create_book,
    delete_book,
    get_book,
    get_books_by_name,
    list_books,
    replace_book,
)
from domain.repositories import BookRepository

router = APIRouter()


@router.get("/books")
def list_books_endpoint(repo: Annotated[BookRepository, Depends(get_book_repo)]):
    """List all books."""
    return [book_to_dict(b) for b in list_books(repo)]


@router.get("/books/{book_id}")
def get_book_endpoint(
    book_id: str, repo: Annotated[BookRepository, Depends(get_book_repo)]
):
    """Get a book by id."""
    book = get_book(repo, book_id)
    if book is not None:
        return book_to_dict(book)
    raise HTTPException(status_code=404, detail="Not found")


@router.get("/books/by-name/{name}")
def get_books_by_name_endpoint(
    name: str, repo: Annotated[BookRepository, Depends(get_book_repo)]
):
    """Search books by name (case-insensitive substring match)."""
    return [book_to_dict(b) for b in get_books_by_name(repo, name)]


@router.post("/books")
def create_book_endpoint(
    book: BookPayload, repo: Annotated[BookRepository, Depends(get_book_repo)]
):
    """Create a book."""
    created = create_book(
        repo,
        name=book.name,
        author=book.author,
        description=book.description,
        url=book.url,
        content=book.content,
    )
    return book_to_dict(created)


@router.put("/books/{book_id}")
def replace_book_endpoint(
    book_id: str,
    book: BookPayload,
    repo: Annotated[BookRepository, Depends(get_book_repo)],
):
    """Replace a book (PUT semantics)."""
    updated = replace_book(
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
def delete_book_endpoint(
    book_id: str, repo: Annotated[BookRepository, Depends(get_book_repo)]
):
    """Delete a book."""
    existing = get_book(repo, book_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Not found")

    deleted = delete_book(repo, book_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Not found")
    return {"deleted": book_to_dict(existing)}
