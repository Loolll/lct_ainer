from fastapi import FastAPI
import uvicorn
import os

from .routes import router


def main():
    app = FastAPI()
    app.include_router(router)

    uvicorn.run(
        app,
        host=os.environ.get('BACKEND_HOST'),
        port=int(os.environ.get('BACKEND_PORT'))
    )
