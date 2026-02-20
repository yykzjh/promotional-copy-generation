"""Application entry point."""

import uvicorn
from fastapi import FastAPI

from .api.routes import router
from .config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title="Promotional Copy Generation",
        description="AI Agent for generating promotional copy with LangGraph, Skills and MCP",
        version="0.1.0",
    )
    app.include_router(router)
    return app


app = create_app()


def main():
    uvicorn.run(
        "promotional_copy_generation.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


if __name__ == "__main__":
    main()
