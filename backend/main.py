import os
import sys
import asyncio
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import router
from backend.database.connection import engine, Base

# --- WINDOWS ASYNCIO FIX ---
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
# -------------------------------

# LOAD ENVIRONMENT VARIABLES FIRST!
load_dotenv()

# Create SQLite database tables if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Product Insights Agent API",
    description="API for running browser-use agent to scrape product reviews."
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the routes we defined
app.include_router(router)

@app.get("/")
def health_check():
    return {"status": "Backend is running!"}