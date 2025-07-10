
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import get_session, create_db_and_tables
from . import models # Don't delete because the tables won't create
from .routers import posts, users, auth, votes

get_session()
# create_db_and_tables() Alembic does it for us

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware, # Middleware: A function that runs before any request
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(posts.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(votes.router)

@app.get("/")
def root():
    return {"message": "welcome to my api"}


