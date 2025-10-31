from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.User.user_router import router as user_router
from src.Author.author_router import arouter as author_router
from src.Student.student_router import srouter as student_router







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
    app.include_router(user_router, prefix='/user', tags=['user'])
    app.include_router(author_router, prefix='/author', tags=['author'])
    app.include_router(student_router, prefix='/student', tags=['student'])
    return app