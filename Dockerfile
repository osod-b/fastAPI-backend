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