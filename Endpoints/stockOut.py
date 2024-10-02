from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from db.VerifyToken import user_dependency
from typing import Optional
from datetime import datetime,timedelta
from db.connection import db_dependency
from models.userModels import StockOut, Products,Stock,StockHistory
from schemas.stockInSchema import StockCreateSchema, StockUpdateSchema, StockResponseSchema

router = APIRouter(prefix="/stock/out", tags=["Stock Out Management"])
@router.post("/add", status_code=201)
async def create_stock_out(stock: StockCreateSchema, db: db_dependency, user: user_dependency):
    if isinstance(user, HTTPException):
        raise user

    """
    Endpoint to create a new stock out entry.
    - **product_id**: ID of the product (required).
    - **product_quantity**: Quantity of the product to stock out (required).
    - **price_per_unit**: Price per unit (required).
    - **total_price**: Total price (optional, calculated from product_quantity * price_per_unit).
    - **date**: Date when the stock was removed (optional).
    """

    # Check if the product exists in the Products table
    product = db.query(Products).filter(Products.Pro_id == stock.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product with this ID does not exist.")

    # Check if sufficient stock exists in Stock (StockIn)
    stockInCurrent = db.query(Stock).filter(Stock.product_id == stock.product_id).first()
    if not stockInCurrent:
        raise HTTPException(status_code=404, detail="No stock entry found for this product in StockIn.")

    purchase_price = float(stockInCurrent.price_per_unit)  # Price per unit at which the stock was purchased
    # Check if the quantity being stocked out exceeds the available stock
    if stock.product_quantity > stockInCurrent.product_quantity:
        raise HTTPException(
            status_code=403,
            detail="Insufficient quantity in stock. Cannot stock out more than what's available."
        )

    # Subtract the stocked-out quantity from the current stock or delete if stock is exhausted
    if stockInCurrent.product_quantity - stock.product_quantity == 0:
        db.delete(stockInCurrent)
    else:
        stockInCurrent.product_quantity -= stock.product_quantity
        stockInCurrent.total_price = str(float(stockInCurrent.product_quantity) * float(stockInCurrent.price_per_unit))

    # Calculate profit or loss
    quantity_sold = stock.product_quantity

    # Profit calculation: (Sales price × quantity) - (Purchase price × quantity)
    # profit = (sales_price * quantity_sold) < (purchase_price * quantity_sold)

    # Determine the profit status
    if (float(stock.product_quantity) * float(stock.price_per_unit)) > (purchase_price * quantity_sold):
        profit_status = "profit"
    elif (float(stock.product_quantity) * float(stock.price_per_unit)) < (purchase_price * quantity_sold):
        profit_status = "loss"
    else:
        profit_status = "break-even"

    # Create a new stock out entry in StockOut
    new_stock_out = StockOut(
        product_id=stock.product_id,
        product_quantity=stock.product_quantity,
        price_per_unit=stock.price_per_unit,
        total_price=str(float(stock.product_quantity) * float(stock.price_per_unit)) if not stock.total_price else stock.total_price,
        date=stock.date
    )

    # Add the stock out entry to StockHistory with type "stock out"
    history = StockHistory(
        product_id=stock.product_id,
        product_quantity=stock.product_quantity,
        price_per_unit=stock.price_per_unit,
        total_price=new_stock_out.total_price,
        stocktype="stock out",
    )

    # Update stock and commit changes
    db.add(new_stock_out)
    db.add(history)
    db.commit()
    db.refresh(new_stock_out)

    # Return the response with required product details and profit status
    return {
        "product_id": new_stock_out.product_id,
        "product_name": product.product_name,
        "product_type": product.product_type,
        "product_quantity": new_stock_out.product_quantity,
        "price_per_unit": new_stock_out.price_per_unit,
        "total_price": new_stock_out.total_price,
        "date": new_stock_out.date,
        "profit_status": profit_status
    }

# Get a single stock entry by its ID (including product name and product type)
@router.get("/{stock_id}", response_model=StockResponseSchema, status_code=200)
async def get_stock_out(stock_id: int, db: db_dependency, user: user_dependency):
    if isinstance(user, HTTPException):
        raise user

    """
    Endpoint to retrieve a single stock entry by its ID, including product name and product type.
    - **stock_id**: ID of the stock entry to retrieve.
    """
    # Perform a join to get product details (name and type)
    stock = db.query(StockOut, Products.product_name, Products.product_type).join(Products, StockOut.product_id == Products.Pro_id).filter(StockOut.stock_id == stock_id).first()
    
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

@router.get("/",  status_code=200)
async def get_all_stocks_out(db: db_dependency, user: user_dependency):
    if isinstance(user, HTTPException):
        raise user

    """
    Endpoint to retrieve all stock out entries, including product name, product type, and profit status for each.
    """

    # Get all stock out entries
    stock_outs = db.query(StockOut).all()

    result = []

    # Iterate over each stock out entry and retrieve the related product and stock in details
    for stock_out in stock_outs:
        # Fetch the product details using the product_id from Products table
        product = db.query(Products).filter(Products.Pro_id == stock_out.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product with ID {stock_out.product_id} does not exist.")

        # Fetch the stock in details for the product to calculate the profit
        stock_in = db.query(StockHistory).filter(StockHistory.product_id == stock_out.product_id).first()
        if not stock_in:
            raise HTTPException(status_code=404, detail=f"No stock entry found for product ID {stock_out.product_id}.")

        # Calculate profit or loss
        purchase_price = float(stock_in.price_per_unit)  # Purchase price per unit from StockIn
        sales_price = float(stock_out.price_per_unit)  # Sales price per unit from StockOut
        quantity_sold = stock_out.product_quantity

        # Profit calculation: (Sales price × quantity) - (Purchase price × quantity)
        profit = (sales_price * quantity_sold) - (purchase_price * quantity_sold)

        # Determine profit status
        if profit > 0:
            profit_status = "profit"
        elif profit < 0:
            profit_status = "loss"
        else:
            profit_status = "break-even"

        # Append the formatted response with profit status
        result.append({
            "stock_id": stock_out.stock_id,
            "product_id": stock_out.product_id,
            "product_quantity": stock_out.product_quantity,
            "price_per_unit": stock_out.price_per_unit,
            "total_price": stock_out.total_price,
            "date": stock_out.date,
            "product_name": product.product_name,
            "product_type": product.product_type,
            "profit_status": profit_status
        })

    return result

# Update an existing stock entry by its ID
@router.patch("/{stock_id}", response_model=StockResponseSchema, status_code=200)
async def update_stockOut(stock_id: int, stock_update: StockUpdateSchema, db: db_dependency, user: user_dependency):
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
    stock = db.query(StockOut).filter(StockOut.stock_id == stock_id).first()
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
    db.refresh(StockOut)
    
    return stock

# Delete a stock entry by its ID
@router.delete("/{stock_id}", status_code=204)
async def delete_stock_out(stock_id: int, db: db_dependency, user: user_dependency):
    if isinstance(user, HTTPException):
        raise user

    """
    Endpoint to delete a stock entry by its ID.
    - **stock_id**: ID of the stock entry to delete. 
    """
    stock = db.query(StockOut).filter(StockOut.stock_id == stock_id).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock entry not found.")
    
    db.delete(stock)
    db.commit()
    return None

@router.post("/byDate", status_code=200)
async def get_all_stocks_out_by_date(
    db: db_dependency, 
    user: user_dependency, 
    startDate: Optional[str] = None, 
    endDate: Optional[str] = None
):
    if isinstance(user, HTTPException):
        raise user

    """
    Endpoint to retrieve all stock out entries by date, including product name, product type, 
    remaining quantity, profit status, and stock transaction type.
    If no dates are provided, fetch today's stock out entries.
    """

    # If no startDate and endDate provided, default to today's date
    if not startDate:
        startDate = datetime.today().strftime('%Y-%m-%d')
    if not endDate:
        endDate = datetime.today().strftime('%Y-%m-%d')

    # Convert dates to full timestamp range
    start_datetime = datetime.strptime(startDate, '%Y-%m-%d')  # 00:00:00
    end_datetime = datetime.strptime(endDate, '%Y-%m-%d') + timedelta(days=1) - timedelta(seconds=1)  # 23:59:59

    # Get all stock out entries between the provided dates or for today
    stock_outs = db.query(StockHistory).filter(
        StockHistory.date.between(start_datetime, end_datetime)
    ).all()

    if not stock_outs:
        raise HTTPException(status_code=404, detail="No stock out entries found for the provided date range.")

    result = []

    # Iterate over each stock out entry and retrieve the related product and stock in details
    for index, stock_out in enumerate(stock_outs):
        # Fetch the product details using the product_id from Products table
        product = db.query(Products).filter(Products.Pro_id == stock_out.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product with ID {stock_out.product_id} does not exist.")

        # Fetch the stock in details for the product to calculate the profit
        stock_in = db.query(StockHistory).filter(StockHistory.product_id == stock_out.product_id).first()
        remaing_quantity = db.query(Stock).filter(Stock.product_id == stock_out.product_id).first()

        if not stock_in:
            raise HTTPException(status_code=404, detail=f"No stock entry found in StockHistory for product ID {stock_out.product_id}.")

        if not remaing_quantity:
            raise HTTPException(status_code=404, detail=f"No remaining stock found for product ID {stock_out.product_id}.")

        # Calculate profit or loss
        purchase_price = float(stock_in.price_per_unit)  # Purchase price per unit from StockIn
        sales_price = float(stock_out.price_per_unit)  # Sales price per unit from StockOut
        quantity_sold = stock_out.product_quantity

        # Profit calculation: (Sales price × quantity) - (Purchase price × quantity)
        profit = (sales_price * quantity_sold) - (purchase_price * quantity_sold)

        # Determine profit status
        if profit > 0:
            profit_status = "profit"
        elif profit < 0:
            profit_status = "loss"
        else:
            profit_status = "break-even"

        # Append the formatted response with profit status
        result.append({
            "stock_id": stock_out.stock_id,
            "product_id": stock_out.product_id,
            "product_quantity": stock_out.product_quantity,
            "remaing_quantity": remaing_quantity.product_quantity,
            "price_per_unit": stock_out.price_per_unit,
            "total_price": stock_out.total_price,
            "date": stock_out.date,
            "product_name": product.product_name,
            "product_type": product.product_type,
            "profit_status": profit_status,
            "tra_type": stock_outs[index].stocktype
        })

    return result
