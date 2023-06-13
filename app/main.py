"""Module is responsible for launching server in development local area."""

from fastapi import FastAPI

from app.routers import user, authentication, post, comment


app = FastAPI()


app.include_router(post.router)
app.include_router(user.router)
app.include_router(authentication.router)
app.include_router(comment.router)


@app.get("/")
def home():
    return {"Hello": "World"}
