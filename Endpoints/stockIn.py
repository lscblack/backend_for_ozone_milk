from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from db.VerifyToken import user_dependency
from db.connection import db_dependency
from models.userModels import Stock, Products, StockHistory
from schemas.stockInSchema import StockCreateSchema, StockUpdateSchema, StockResponseSchema

router = APIRouter(prefix="/stock/in", tags=["Stock In Management"])
@router.post("/", status_code=201)
async def create_or_update_stock(stock: StockCreateSchema, db: db_dependency, user: user_dependency):
    if isinstance(user, HTTPException):
        raise user

    """
    Endpoint to create or update a stock entry.
    - **product_id**: ID of the product (required).
    - **product_quantity**: Quantity of the product (required).
    - **price_per_unit**: Price per unit (required).
    - **total_price**: Total price (optional, calculated from product_quantity * price_per_unit).
    - **date**: Date when the stock was added (optional).
    """

    # Check if the product exists
    product = db.query(Products).filter(Products.Pro_id == stock.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product with this ID does not exist.")

    # Check if stock for this product already exists
    existing_stock = db.query(Stock).filter(Stock.product_id == stock.product_id).first()

    if existing_stock:
        # If stock exists, update its quantity, prices, and date
        existing_stock.product_quantity += stock.product_quantity
        existing_stock.price_per_unit = stock.price_per_unit
        existing_stock.total_price = str(float(existing_stock.product_quantity) * float(stock.price_per_unit))
        existing_stock.date = stock.date
        db.commit()
        db.refresh(existing_stock)

        # Add to stock history as an update
        history = StockHistory(
            product_id=stock.product_id,
            product_quantity=stock.product_quantity,
            price_per_unit=stock.price_per_unit,
            total_price=existing_stock.total_price,
            stocktype="stock update",
        )
        db.add(history)
        db.commit()

        return {
            "message": "Stock updated successfully",
            "product_id": existing_stock.product_id,
            "product_name": product.product_name,
            "product_type": product.product_type,
            "product_quantity": existing_stock.product_quantity,
            "price_per_unit": existing_stock.price_per_unit,
            "total_price": existing_stock.total_price,
            "date": existing_stock.date
        }
    else:
        # Create new stock since it doesn't exist
        new_stock = Stock(**stock.dict())
        # Automatically calculate total price if not provided
        if not stock.total_price:
            new_stock.total_price = str(float(stock.product_quantity) * float(stock.price_per_unit))

        # Add to stock history as a new stock entry
        history = StockHistory(
            product_id=stock.product_id,
            product_quantity=stock.product_quantity,
            price_per_unit=stock.price_per_unit,
            total_price=new_stock.total_price,
            stocktype="stock in",
        )

        # Add new stock and its history to the database
        db.add(new_stock)
        db.add(history)
        db.commit()
        db.refresh(new_stock)

        return {
            "message": "Stock created successfully",
            "product_id": new_stock.product_id,
            "product_name": product.product_name,
            "product_type": product.product_type,
            "product_quantity": new_stock.product_quantity,
            "price_per_unit": new_stock.price_per_unit,
            "total_price": new_stock.total_price,
            "date": new_stock.date
        }


# Get a single stock entry by its ID (including product name and product type)
@router.get("/{stock_id}", response_model=StockResponseSchema, status_code=200)
async def get_stock(stock_id: int, db: db_dependency, user: user_dependency):
    if isinstance(user, HTTPException):
        raise user

    """
    Endpoint to retrieve a single stock entry by its ID, including product name and product type.
    - **stock_id**: ID of the stock entry to retrieve.
    """
    # Perform a join to get product details (name and type)
    stock = db.query(Stock, Products.product_name, Products.product_type).join(Products, Stock.product_id == Products.Pro_id).filter(Stock.stock_id == stock_id).first()
    
    if not stock:
        raise HTTPException(status_code=404, detail="Stock entry not found.")

    # Unpack the query result
    stock_entry, product_name, product_type = stock

    return {
        "stock_id": stock_entry.stock_id,
        "product_id": stock_entry.product_id,
        "product_quantity": stock_entry.product_quantity,
        "price_per_unit": stock_entry.price_per_unit,
        "total_price": stock_entry.total_price,
        "date": stock_entry.date,
        "product_name": product_name,
        "product_type": product_type
    }

# Get all stock entries
@router.get("/", response_model=list[StockResponseSchema], status_code=200)
async def get_all_stocks(db: db_dependency, user: user_dependency):
    if isinstance(user, HTTPException):
        raise user

    """
    Endpoint to retrieve all stock entries, including product name and product type for each.
    """
    stocks = db.query(Stock, Products.product_name, Products.product_type).join(Products, Stock.product_id == Products.Pro_id).all()

    # Unpack and format the response
    return [
        {
            "stock_id": stock.stock_id,
            "product_id": stock.product_id,
            "product_quantity": stock.product_quantity,
            "price_per_unit": stock.price_per_unit,
            "total_price": stock.total_price,
            "date": stock.date,
            "product_name": product_name,
            "product_type": product_type
        }
        for stock, product_name, product_type in stocks
    ]

# Update an existing stock entry by its ID
@router.patch("/{stock_id}", response_model=StockResponseSchema, status_code=200)
async def update_stock(stock_id: int, stock_update: StockUpdateSchema, db: db_dependency, user: user_dependency):
    if isinstance(user, HTTPException):
        raise user

    """
    Endpoint to update an existing stock entry by its ID.
    - **stock_id**: ID of the stock entry to update.
    - **product_quantity**: (optional) Updated quantity of the product.
    - **price_per_unit**: (optional) Updated price per unit.
    - **total_price**: (optional) Updated total price.
    - **date**: (optional) Updated date of stock entry.
    """
    stock = db.query(Stock).filter(Stock.stock_id == stock_id).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock entry not found.")
    
    if stock_update.product_quantity is not None:
        stock.product_quantity = stock_update.product_quantity
    if stock_update.price_per_unit is not None:
        stock.price_per_unit = stock_update.price_per_unit
    if stock_update.total_price is not None:
        stock.total_price = stock_update.total_price
    if stock_update.date:
        stock.date = stock_update.date
    
    db.commit()
    db.refresh(stock)
    
    return stock

# Delete a stock entry by its ID
@router.delete("/{stock_id}", status_code=204)
async def delete_stock(stock_id: int, db: db_dependency, user: user_dependency):
    if isinstance(user, HTTPException):
        raise user

    """
    Endpoint to delete a stock entry by its ID.
    - **stock_id**: ID of the stock entry to delete.
    """
    stock = db.query(Stock).filter(Stock.stock_id == stock_id).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock entry not found.")
    
    db.delete(stock)
    db.commit()
    return None
