# -fastAPI-backend
[GitHub Pages]() \ 
Backend API with JWT tokens, MFA, CRUD, sort of architecture with layer separation.


## Local deployment
```
docker build -t app .
docker run -p 8000:8000 app

Docs: http://localhost:8000/docs
```
## Docker Image
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
### Prerequisites
```
Python
Docker
```

## Project Structure

```

```
## Tech Stack


##  


### .env.example variables
```
...
```


##
[Auth Endpoints]('controllers/authController.py')
