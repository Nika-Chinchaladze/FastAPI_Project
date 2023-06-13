from fastapi import FastAPI

from app.routers import user, authentication, post


app = FastAPI()


app.include_router(post.router)
app.include_router(user.router)
app.include_router(authentication.router)


@app.get("/")
def home():
    return {"Hello": "World"}
