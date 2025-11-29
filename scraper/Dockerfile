FROM python:3.12.8-slim

ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y procps && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /scraper

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd appuser && \
    chown -R appuser:appuser /scraper
   
USER appuser

CMD ["sh", "-c", "python3 main.py"]
