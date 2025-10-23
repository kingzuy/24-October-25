FROM ubuntu:22.04

RUN apt update && apt install -y \
    python3 \
    python3-pip \
    nginx \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install flask gunicorn

WORKDIR /app
COPY app.py .
COPY requirements.txt .

# CRITICAL VULNERABILITY: Run as root
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
