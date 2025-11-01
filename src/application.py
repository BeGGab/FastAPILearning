from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.user.router import router as user_router
from src.author.router import router as author_router
from src.student.router import router as student_router







def get_app() -> FastAPI:
    """
    Get FastAPI application.

    This is the main constructor of an application.

    :return: application.
    """
    app = FastAPI(
        docs_url='/docs',
        openapi_url='/openapi.json',
        default_response_class=JSONResponse,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[],  # Указывайте здесь домены вашего фронтенда
        allow_credentials=True,
        allow_origin_regex=r"http://localhost:.*",  # Для локальной разработки
        allow_methods=['*'],
        allow_headers=['*'],
    )
    app.include_router(user_router)
    app.include_router(author_router)
    app.include_router(student_router)
    return app