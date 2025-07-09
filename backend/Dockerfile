FROM python:3.10-alpine

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TEMP_DIR=/tmp/optimizer \
    MAX_FILE_SIZE=52428800 \
    PORT=8000

WORKDIR /app

# Install system dependencies - including libstdc++ from edge repository
RUN apk add --no-cache --virtual .build-deps \
    gcc \
    musl-dev \
    python3-dev \
    libffi-dev \
    openssl-dev \
    g++ \
    # Add libstdc++ from edge repository
    && apk add --no-cache --repository=http://dl-cdn.alpinelinux.org/alpine/edge/main libstdc++ \
    # Runtime dependencies
    && apk add --no-cache \
    bash \
    # Create temp directory
    && mkdir -p ${TEMP_DIR} \
    && chmod 777 ${TEMP_DIR}

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    # Clean up build dependencies
    && apk del .build-deps

# Copy application code
COPY . .

EXPOSE ${PORT}

# Use a non-root user for security
RUN adduser -D appuser && chown -R appuser:appuser /app
USER appuser

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]