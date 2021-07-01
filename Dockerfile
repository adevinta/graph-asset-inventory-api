FROM python:3.9.6-alpine

# Install system dependencies.
RUN apk add gcc musl-dev

# Set workdir to /app.
WORKDIR /app

# Install Python requirements.
COPY requirements/requirements.txt .
RUN pip install -r requirements.txt && rm -f requirements.txt

# Copy service code.
COPY graph_asset_inventory_api graph_asset_inventory_api

# Set Python's class path
ENV PYTHONPATH=/app

# Execute gunicorn as entry point.
ENTRYPOINT ["gunicorn", "graph_asset_inventory_api.app:conn_app"]
