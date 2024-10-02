from fastapi import APIRouter, HTTPException
from typing import List
from db.connection import db_dependency
from db.VerifyToken import user_dependency
from models.userModels import Balance
from schemas.schemas import BalanceCreateSchema, BalanceResponseSchema

router = APIRouter(prefix="/balance", tags=["Balance Management"])

# Create balance entry (either opening or closing)
@router.post("/add", response_model=BalanceResponseSchema, status_code=201)
async def create_balance(balance: BalanceCreateSchema, db: db_dependency, user:user_dependency):
    if isinstance(user, HTTPException):
        raise user

    db_balance = Balance(
        balance_type=balance.balance_type,
        date=balance.date if balance.date else datetime.utcnow(),
        cash_balance=balance.cash_balance,
        momo_balance=balance.momo_balance
    )
    db.add(db_balance)
    db.commit()
    db.refresh(db_balance)
    return db_balance

# Get all balances
@router.get("/", response_model=List[BalanceResponseSchema])
async def get_all_balances(db: db_dependency,user:user_dependency):
    if isinstance(user, HTTPException):
        raise user
    balances = db.query(Balance).all()
    return balances

# Get a single balance by ID
@router.get("/{balance_id}", response_model=BalanceResponseSchema)
async def get_balance(balance_id: int, db: db_dependency,user:user_dependency):
    if isinstance(user, HTTPException):
        raise user
    balance = db.query(Balance).filter(Balance.id == balance_id).first()
    if not balance:
        raise HTTPException(status_code=404, detail="Balance not found")
    return balance
