FROM nginx:alpine
# FROM python:3.6-alpine

WORKDIR /my_django-demo

COPY main.py .
COPY util.zip .

RUN apk update && \
    apk add --update --no-cache ca-certificates python3 && \
    chmod +x main.py

EXPOSE 8080

CMD ["python3", "main.py"]