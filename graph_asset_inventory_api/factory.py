"""This module provides the Connexion App factory of the API."""

import os
import sys
import logging
from logging.config import dictConfig

import connexion

from graph_asset_inventory_api.context import close_inventory_client


def config_logger():
    """Configures the Flask logger."""

    flask_env = os.getenv('FLASK_ENV', 'development')
    log_level = logging.DEBUG if flask_env == 'development' else logging.INFO

    dictConfig({
        'version': 1,
        'formatters': {
            'default': {
                'format':
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            }
        },
        'handlers': {
            'stderr': {
                'class': 'logging.StreamHandler',
                'stream': sys.stderr,
                'formatter': 'default'
            }
        },
        'root': {
            'level': log_level,
            'handlers': ['stderr']
        }
    })


def config_db(app):
    """Configures the Graph DB. Reading the neptune endpoint from the
    environment."""

    neptune_endpoint = os.getenv('NEPTUNE_ENDPOINT', None)
    if neptune_endpoint is None:
        raise 'missing env var NEPTUNE_ENDPOINT'

    app.config['NEPTUNE_ENDPOINT'] = neptune_endpoint
    app.teardown_appcontext(close_inventory_client)


def create_app():
    """Returns a new Connection App."""

    # It is recommended to configure the logger as soon as possible (i.e.
    # before creating the application object).
    config_logger()

    conn_app = connexion.App(__name__, specification_dir='openapi/')
    conn_app.add_api('graph-asset-inventory-api.yaml', resolver_error=501)

    config_db(conn_app.app)

    return conn_app
