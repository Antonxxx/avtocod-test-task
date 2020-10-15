FROM python:3.8-alpine
ENV PYTHONPATH=/app
WORKDIR /app/avtocod-test-task
COPY requirements.txt .
RUN apk add --no-cache --virtual .build-deps build-base libffi-dev libxml2-dev libxslt-dev\
    && apk add --no-cache bash\
    && pip install -U pip \
    && pip install --no-cache-dir -r requirements.txt
COPY app.py .