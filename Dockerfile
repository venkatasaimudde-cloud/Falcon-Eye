FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for OpenCV and MediaPipe
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Run database migration / seeds and generate sample media
RUN python sample_data/seed_db.py && python sample_data/generate_samples.py

# Expose port (default 8000)
EXPOSE 8000

ENV PORT=8000
ENV HOST=0.0.0.0

CMD ["python", "run.py"]
