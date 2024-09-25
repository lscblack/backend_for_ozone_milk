from fastapi import APIRouter, HTTPException
from dotenv import load_dotenv
from db.VerifyToken import user_dependency
from db.connection import db_dependency



# Load environment variables from .env file
load_dotenv()

router = APIRouter(prefix="/diseases", tags=["Diseases Management"])

@router.get("/all", status_code=200)
async def get_all_diseases(user: user_dependency, db:db_dependency):
    return "hello"