FROM python:3.11-slim
WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app

ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=exam_system.settings

RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

CMD ["gunicorn", "exam_system.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
