import logging
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Linux OS NL2SH RAG Tool",
    description="HTTP adapter for Linux OS NL2SH RAG Tool",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
async def root():
    return {
        "service": "SQL Agent MCP Web Adapter",
        "status": "running",
        "description": "HTTP adapter for MCP SQL Agent server",
        "endpoints": [
            "GET /",
        ]
    }

if __name__ == "__main__":
    logger.info("Starting Linux OS NL2SH RAG Tool...")
    uvicorn.run(app, host="0.0.0.0", port=8000)