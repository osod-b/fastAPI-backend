from fastapi import FastAPI
from app.middle import add_middleware, add_ratelimiter_middleware, add_signature_middlware, add_ip_catcher_middleware

from controllers.crudController import crud
from controllers.filesController import files
from controllers.logInController import login
from controllers.signUpController import sign

from contextlib import asynccontextmanager

from db.schema import init_db
from models.client import ClientModel
from models.user import UserModel

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(title='Backend Application',
              lifespan=lifespan,
              description='Multifunctional backend API for CRUD operations, authentication, and database management.'
            )

add_middleware(app)
add_ratelimiter_middleware(app)
add_signature_middlware(app)
add_ip_catcher_middleware(app)

app.include_router(login)
app.include_router(sign)
app.include_router(crud)
app.include_router(files)