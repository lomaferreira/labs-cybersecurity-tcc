FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir flask bcrypt

COPY app.py .
COPY templates/ ./templates/

EXPOSE 5000

CMD ["python", "app.py"]
