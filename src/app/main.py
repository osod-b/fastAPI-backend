from fastapi import FastAPI
from app.middle import add_middleware, add_ratelimiter_middleware, add_signature_middlware, add_ip_catcher_middleware
from controllers.authController import auth
from controllers.crudController import crud
from controllers.filesController import files

from db.schema import Base, main_engine
from models.user import UserModel
from models.client import ClientModel

Base.metadata.create_all(bind=main_engine)

app = FastAPI(title='Backend Application', description='Multifunctional backend API for CRUD operations, authentication, and database management.')


add_middleware(app)
add_ratelimiter_middleware(app)
add_signature_middlware(app)
add_ip_catcher_middleware(app)

app.include_router(auth)
app.include_router(crud)
app.include_router(files)





#-----ENDPOINTS--------
#implement cachinch database (but I'm still not sure.)


