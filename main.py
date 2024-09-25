from enum import Enum
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from Endpoints import auth,stock,stockIn

app = FastAPI(
    title="Ozone Milk Api Documentation",  # Replace with your desired title
    description="Stock Management",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to the specific origins you want to allow
    allow_credentials=True,
    allow_methods=["*"],  # Adjust this to the specific methods you want to allow (e.g., ["GET", "POST"])
    allow_headers=["*"],  # Adjust this to the specific headers you want to allow (e.g., ["Content-Type", "Authorization"])
)

# Include the routers from auth, apis, and otp
app.include_router(auth.router)
app.include_router(stock.router)
app.include_router(stockIn.router)
# app.include_router(diseases.router)
