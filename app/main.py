from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import auth, likes, post, user

# models.Base.metadata.create_all(bind=engine)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(likes.router)


@app.get("/")
def root():
    return {"message": "Hello World babysss!"}
