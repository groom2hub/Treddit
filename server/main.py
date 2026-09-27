# backend/main.py
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

import nlp
from config import settings

# JVM(konlpy)은 반드시 메인 스레드에서 시작해야 종료 시 멈추지 않는다 (nlp.okt 참고)
nlp.okt()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api = APIRouter(prefix="/api")

@api.get("/")
def read_root():
    return {"Hello": "Hello World"}

@api.get("/home")
def read_root1():
    return {"Home": "Welcome"}

@api.get("/health")
def health():
    return {"status": "ok"}


from user import user_router
from post import post_router
from comment import comment_router
from service import service_router
from google_keyword import google_keyword_router
from realtime_keyword import realtime_keyword_router

api.include_router(user_router.router, tags=["user"])
api.include_router(post_router.router, tags=["post"])
api.include_router(comment_router.router, tags=["comment"])
api.include_router(service_router.router, tags=["service"])
api.include_router(google_keyword_router.router, tags=["keyword"])
api.include_router(realtime_keyword_router.router, tags=["keyword2"])

app.include_router(api)

if __name__ == "__main__":
	import uvicorn
	uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
