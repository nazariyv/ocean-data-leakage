FROM python:3.8.3-alpine3.12

WORKDIR /app

COPY ./filter/ /app/

# CMD [ "pip install -r requirements.txt --no-cache-dir --no-color" ]

ENTRYPOINT ["python", "/app/main.py"]
