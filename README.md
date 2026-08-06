# -fastAPI-backend
Backend API with JWT tokens, MFA, CRUD, layer separation.

## Local deployment
```
docker build -t app .
docker run -p 8000:8000 app

Docs: http://localhost:8000/docs
```

## Navigation
[Auth Endpoints (LogIn)](src/controllers/logInController.py) \
\
[Auth Endpoints (SignUp)](src/controllers/signUpController.py) \
\
[Crud Endpoints](src/controllers/crudController.py) \
\
[Files Endpoints](src/controllers/filesController.py)  

<!-- [View Endpoints](src/controllers/viewController.py)   -->


## Docker Image Configuration
```
FROM python:3.12-slim
WORKDIR /

RUN apt-get update && apt-get install -y --no-install-recommends redis-server \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ./src ./src
COPY ./storage ./storage
COPY .env ./

COPY src/docker-run.sh /src/docker-run.sh
RUN chmod +x /src/docker-run.sh

WORKDIR ./src
CMD ["/src/docker-run.sh"]
```

## Prerequisites
- Python
- Docker
- Redis
- Git
  
## Requirements.txt
- FastAPI
- Uvicorn
- SQLALchemy
- SQLModel
- Pydantic
- Passlib
- Pandas
- PyJWT
- Pytest
- Bcrypt
- Cryptography
- AioSqlite
- Datafaker



## Project Structure
```
|──src/
    |──app/
        |──middleware
        main.py
        middle.py
        redis.py
        logger.py
    |──controllers/
         crudController.py
         filesController.py
         logInController.py
         signUpController.py
         viewController.py
    |──core/
        config.py
    |──db/
        schema.py
    |──models
        client.py
        user.py
    |──schemas
        client.py
        user.py
    |──services
        adminService.py
        authService.py
        crudService.py
        filesService.py
        jwtService.py
        viewService.py
    |──tests
        |──unit
            auth.py
        |──integ
            auth.py
    |──utils
        repositories.py
        authHelpers.py
        crudHelpers.py
        filesHelpers.py
    |──validators
        clients.py
        users.py
|──storage/
    |──exports/
    |──imports/
```
