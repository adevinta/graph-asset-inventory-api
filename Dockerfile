# Builder stage for getting amanzon-neptune-tools.
FROM python:3.9.6-alpine as builder

RUN apk add git

RUN git clone --depth 1 --branch amazon-neptune-tools-1.4 \
	https://github.com/awslabs/amazon-neptune-tools /amazon-neptune-tools


# Stage for the graph-asset-inventory-api image.
FROM python:3.9.6-alpine

RUN apk add gcc g++ musl-dev libffi-dev

RUN mkdir -p /app
WORKDIR /app

COPY requirements/requirements.txt .
RUN pip install -r requirements.txt && rm -f requirements.txt

RUN mkdir -p /deps
COPY --from=builder \
	/amazon-neptune-tools/neptune-python-utils/neptune_python_utils \
	/deps/neptune_python_utils

ENV PYTHONPATH="/app:/deps"

ENTRYPOINT ["gunicorn", "graph_asset_inventory_api.app:create_app()"]
