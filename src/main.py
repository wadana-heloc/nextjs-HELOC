
from fastapi import Depends, FastAPI, HTTPException

from database import Base, engine

import models  

app = FastAPI()


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health_check():
    return {"status": "ok"}
