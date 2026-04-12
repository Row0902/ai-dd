import json
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

DATA_FILE = Path(__file__).parent / "library.json"


def load_data():
    if not DATA_FILE.exists():
        return []
    try:
        with open(DATA_FILE, encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, list):
                return []
            return data
    except Exception:
        return []


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


app = FastAPI()


class Book(BaseModel):
    name: str
    author: str = ""
    description: str = ""
    url: str = ""
    content: str = ""


@app.get("/")
def root():
    return {"msg": "AI Driven Development - biblioteca digital"}


@app.get("/books")
def list_books():
    return load_data()


@app.get("/books/{book_id}")
def get_book(book_id: str):
    data = load_data()
    for b in data:
        if b.get("id") == book_id:
            return b
    raise HTTPException(status_code=404, detail="Not found")


@app.get("/books/by-name/{name}")
def get_books_by_name(name: str):
    data = load_data()
    res = []
    for b in data:
        if name.lower() in (b.get("name") or "").lower():
            res.append(b)
    return res


@app.post("/books")
def create_book(book: Book):
    data = load_data()
    new = {
        "id": uuid.uuid4().hex,
        "name": book.name,
        "author": book.author,
        "description": book.description,
        "url": book.url,
        "content": book.content,
    }
    data.append(new)
    save_data(data)
    return new


@app.put("/books/{book_id}")
def update_book(book_id: str, book: Book):
    data = load_data()
    for idx, b in enumerate(data):
        if b.get("id") == book_id:
            data[idx].update(
                {
                    "name": book.name,
                    "author": book.author,
                    "description": book.description,
                    "url": book.url,
                    "content": book.content,
                }
            )
            save_data(data)
            return data[idx]
    raise HTTPException(status_code=404, detail="Not found")


@app.delete("/books/{book_id}")
def delete_book(book_id: str):
    data = load_data()
    for idx, b in enumerate(data):
        if b.get("id") == book_id:
            removed = data.pop(idx)
            save_data(data)
            return {"deleted": removed}
    raise HTTPException(status_code=404, detail="Not found")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
