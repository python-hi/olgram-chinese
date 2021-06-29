FROM python:3.8-buster

COPY . /app

WORKDIR /app

RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \

CMD ["python", "instance"]
