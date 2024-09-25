from enum import Enum
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from Endpoints import auth

app = FastAPI(
    title="AfiaCare Api Documentation",  # Replace with your desired title
    description="Afiacare aims to revolutionize healthcare management in Cameroon by providing a comprehensive digital platform. This platform will address common issues like data mismanagement, donor matching, and information sharing between hospitals. By leveraging technology, Afiacare will enhance the accuracy, efficiency, and accessibility of healthcare services.",
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
# app.include_router(counts.router)
# app.include_router(diseases.router)
