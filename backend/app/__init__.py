from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn
import os

from .routes import router


def main():
    app = FastAPI()
    app.include_router(router)
    app.mount("/static", StaticFiles(directory="/share/static"), name="static")
    uvicorn.run(
        app,
        host=os.environ.get('BACKEND_HOST'),
        port=int(os.environ.get('BACKEND_PORT'))
    )
