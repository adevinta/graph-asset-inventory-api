import os
import sys
import logging

import connexion


def create_app():
    conn_app = connexion.App(__name__, specification_dir='openapi/')
    conn_app.add_api('graph-asset-inventory-api.yaml', resolver_error=501)

    log_level = logging.DEBUG if conn_app.app.debug else logging.INFO
    conn_app.app.logger.setLevel(log_level)

    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    conn_app.app.logger.handlers.clear()
    conn_app.app.logger.addHandler(handler)

    return conn_app
