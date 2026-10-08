import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agentic_platform.api.routes import router
from agentic_platform.config import get_settings

settings = get_settings()
logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))

app = FastAPI(
    title="Governed Enterprise Agentic Platform",
    version="0.1.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["*"] ,
    allow_headers=["*"] ,
)
app.include_router(router)
