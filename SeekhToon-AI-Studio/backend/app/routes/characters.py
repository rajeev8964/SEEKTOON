from fastapi import APIRouter, HTTPException

from ..database import connect
from ..models.requests import CharacterRequest

router = APIRouter(prefix="/api")


@router.get("/characters")
def list_characters():
    with connect() as db:
        rows = db.execute("SELECT * FROM characters ORDER BY id DESC").fetchall()
    return [dict(row) for row in rows]


@router.post("/characters")
def create_character(req: CharacterRequest):
    with connect() as db:
        cursor = db.execute(
            "INSERT INTO characters(name, description, style) VALUES (?, ?, ?)",
            (req.name, req.description, req.style),
        )
        row = db.execute(
            "SELECT * FROM characters WHERE id=?", (cursor.lastrowid,)
        ).fetchone()
    return dict(row)


@router.delete("/characters/{character_id}")
def delete_character(character_id: int):
    with connect() as db:
        cursor = db.execute("DELETE FROM characters WHERE id=?", (character_id,))
        if cursor.rowcount == 0:
            raise HTTPException(404, "Character not found")
    return {"deleted": character_id}
