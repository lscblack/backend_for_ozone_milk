from fastapi import APIRouter, HTTPException
from dotenv import load_dotenv
from db.VerifyToken import user_dependency
from db.connection import db_dependency
from models.userModels import Products 

from schemas.stockSchema import ProductCreateSchema, ProductUpdateSchema, ProductResponseSchema

router = APIRouter(prefix="/products", tags=["Product Management"])

# Create a new product
@router.post("/", response_model=ProductResponseSchema, status_code=201)
async def create_product(product: ProductCreateSchema, db:db_dependency,user:user_dependency):
    if isinstance(user, HTTPException):
        raise user
    """
    Endpoint to create a new product in the database.
    - **product_name**: Name of the product (required).
    - **product_price**: Price of the product (optional).
    - **date**: Date the product was added (optional).
    """
    # Check for product name uniqueness
    existing_product = db.query(Products).filter(Products.product_name == product.product_name).first()
    if existing_product:
        raise HTTPException(status_code=400, detail="Product with this name already exists.")
    
    new_product = Products(**product.dict())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product

# Get a single product by its ID
@router.get("/{product_id}", response_model=ProductResponseSchema, status_code=200)
async def get_product(product_id: int, db:db_dependency,user:user_dependency):
    if isinstance(user, HTTPException):
        raise user
    """
    Endpoint to retrieve a single product by its ID.
    - **product_id**: ID of the product to retrieve.
    """
    product = db.query(Products).filter(Products.pro_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")
    
    return product

# Get all products
@router.get("/", response_model=list[ProductResponseSchema], status_code=200)
async def get_all_products(db:db_dependency,user:user_dependency):
    if isinstance(user, HTTPException):
        raise user
    """
    Endpoint to retrieve all products.
    """
    products = db.query(Products).all()
    return products

# Update an existing product by its ID
@router.patch("/{product_id}", response_model=ProductResponseSchema, status_code=200)
async def update_product(product_id: int, product_update: ProductUpdateSchema, db:db_dependency,user:user_dependency):
    if isinstance(user, HTTPException):
        raise user
    """
    Endpoint to update an existing product by its ID.
    - **product_id**: ID of the product to update.
    - **product_name**: (optional) Updated name of the product.
    - **product_price**: (optional) Updated price of the product.
    - **date**: (optional) Updated date the product was added.
    """
    product = db.query(Products).filter(Products.pro_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")
    
    # Update fields
    if product_update.product_name:
        product.product_name = product_update.product_name
    if product_update.product_price:
        product.product_price = product_update.product_price
    if product_update.date:
        product.date = product_update.date
    
    db.commit()
    db.refresh(product)
    
    return product

# Delete a product by its ID
@router.delete("/{product_id}", status_code=204)
async def delete_product(product_id: int, db:db_dependency,user:user_dependency):
    if isinstance(user, HTTPException):
        raise user
    """
    Endpoint to delete a product by its ID.
    - **product_id**: ID of the product to delete.
    """
    product = db.query(Products).filter(Products.pro_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")
    
    db.delete(product)
    db.commit()
    return None
