from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from db.VerifyToken import user_dependency
from typing import List
from datetime import datetime
from db.connection import db_dependency
from models.userModels import Transaction
from schemas.schemas import TransactionCreate, TransactionUpdate, TransactionResponse

router = APIRouter(prefix="/transactions", tags=["Transaction Management"])

@router.post("/", status_code=201, response_model=TransactionResponse)
async def create_transaction(transaction: TransactionCreate, db: db_dependency, user: user_dependency):
    if isinstance(user, HTTPException):
        raise user
    new_transaction = Transaction(**transaction.dict())
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)
    return new_transaction

@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(transaction_id: int, db: db_dependency, user: user_dependency):
    if isinstance(user, HTTPException):
        raise user
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

@router.get("/", response_model=List[TransactionResponse])
async def get_all_transactions(db: db_dependency, user: user_dependency):
    if isinstance(user, HTTPException):
        raise user
    transactions = db.query(Transaction).all()
    return transactions

@router.delete("/{transaction_id}", status_code=204)
async def delete_transaction(transaction_id: int, db: db_dependency, user: user_dependency):
    if isinstance(user, HTTPException):
        raise user
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    db.delete(transaction)
    db.commit()
    return {"message": "Transaction deleted successfully"}

@router.patch("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(transaction_id: int, transaction_update: TransactionUpdate, db: db_dependency, user: user_dependency):
    if isinstance(user, HTTPException):
        raise user
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    for key, value in transaction_update.dict(exclude_unset=True).items():
        setattr(transaction, key, value)
    
    db.commit()
    db.refresh(transaction)
    return transaction