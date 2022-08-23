FROM python:3.9.12-alpine3.15 as python-base
RUN apk add gcc g++ musl-dev libffi-dev


FROM python-base as pip-compile
ARG PIP_TOOLS_VERSION=6.5.1
RUN pip install "pip-tools==${PIP_TOOLS_VERSION}"
ENTRYPOINT ["pip-compile"]


FROM python-base as amazon-neptune-tools
ARG AMAZON_NEPTUNE_TOOLS_VERSION=1.12
RUN apk add git
RUN git clone --depth 1 --branch "amazon-neptune-tools-${AMAZON_NEPTUNE_TOOLS_VERSION}" https://github.com/awslabs/amazon-neptune-tools /amazon-neptune-tools


FROM python-base as service-base
RUN mkdir -p /app
WORKDIR /app
RUN mkdir -p /deps
COPY --from=amazon-neptune-tools \
	/amazon-neptune-tools/neptune-python-utils/neptune_python_utils \
	/deps/neptune_python_utils
ENV PYTHONPATH="/app:/deps"


FROM service-base as dev
COPY requirements/requirements-dev.txt /tmp/
RUN pip install -r /tmp/requirements-dev.txt && rm -f /tmp/requirements-dev.txt


FROM service-base
COPY requirements/requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt && rm -f /tmp/requirements.txt
COPY graph_asset_inventory_api /app/graph_asset_inventory_api
ENTRYPOINT ["gunicorn", "graph_asset_inventory_api.app:create_app()"]
