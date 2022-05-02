# Builder stage for getting amanzon-neptune-tools.
FROM python:3.9.12-alpine3.15 as builder

RUN apk add git

RUN git clone --depth 1 --branch amazon-neptune-tools-1.7 \
	https://github.com/awslabs/amazon-neptune-tools /amazon-neptune-tools


# Stage for the graph-asset-inventory-api image.
FROM python:3.9.12-alpine3.15

RUN apk add gcc g++ musl-dev libffi-dev

COPY requirements/requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt && rm -f /tmp/requirements.txt

RUN mkdir -p /app
WORKDIR /app

COPY graph_asset_inventory_api /app/graph_asset_inventory_api

RUN mkdir -p /deps
COPY --from=builder \
	/amazon-neptune-tools/neptune-python-utils/neptune_python_utils \
	/deps/neptune_python_utils

ENV PYTHONPATH="/app:/deps"

ENTRYPOINT ["gunicorn", "graph_asset_inventory_api.app:create_app()"]
