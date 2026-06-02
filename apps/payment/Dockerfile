FROM python:3.12-alpine

WORKDIR /app
COPY src/server.py /app/server.py

ENV SERVICE_NAME=payment
ENV PORT=8080

EXPOSE 8080

CMD ["python", "/app/server.py"]
