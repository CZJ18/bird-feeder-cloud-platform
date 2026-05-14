from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.crud import get_statistics

router = APIRouter()

@router.get("/statistics")
async def get_statistics_data(db: Session = Depends(get_db)):
    stats = get_statistics(db)
    return {"ok": True, "message": "success", "data": stats}
