FROM python:3.12-slim

WORKDIR /app

# Install system deps
RUN apt-get update && \
    apt-get install -y --no-install-recommends nginx && \
    rm -rf /var/lib/apt/lists/*

# Install Python deps
RUN pip install fastapi uvicorn[standard] pydantic sqlite-utils

# Copy backend and frontend
COPY backend ./backend
COPY frontend ./frontend
COPY nginx/nginx.conf /etc/nginx/nginx.conf

# Serve frontend via symlink
RUN rm -rf /var/www/html && ln -s /app/frontend /var/www/html

EXPOSE 80

# Start backend + nginx
CMD uvicorn backend.main:app --host 0.0.0.0 --port 8000 & nginx -g "daemon off;"
