FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir flask pyopenssl

COPY app.py .
COPY templates/ ./templates/

EXPOSE 5000 5443

CMD ["python", "app.py"]
