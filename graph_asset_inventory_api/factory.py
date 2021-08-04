"""This module provides the Connexion App factory of the API."""

import os
import sys
import logging
from logging.config import dictConfig

import connexion

from graph_asset_inventory_api import EnvVarNotSetError
from graph_asset_inventory_api.context import close_inventory_client


def config_logger(debug=False):
    """Configures the Flask logger."""
    log_level = logging.DEBUG if debug else logging.INFO

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
    """Configures the Graph DB."""
    gremlin_endpoint = os.getenv('GREMLIN_ENDPOINT', None)
    if gremlin_endpoint is None:
        raise EnvVarNotSetError('GREMLIN_ENDPOINT')

    app.config['GREMLIN_ENDPOINT'] = gremlin_endpoint
    app.teardown_appcontext(close_inventory_client)


def config_auth_mode(app):
    """Configures the authentication mode."""
    app.config['GREMLIN_AUTH_MODE'] = os.getenv('GREMLIN_AUTH_MODE', 'none')


def create_app():
    """Returns a new Connection App."""
    # Get flask environment.
    flask_env = os.getenv('FLASK_ENV', 'production')
    debug = (flask_env == 'development')

    # It is recommended to configure the logger as soon as possible (i.e.
    # before creating the application object).
    config_logger(debug)

    conn_app = connexion.App(
        __name__,
        specification_dir='openapi/',
        debug=debug,
    )
    conn_app.add_api(
        'graph-asset-inventory-api.yaml',
        strict_validation=True,
        resolver_error=501,
    )

    config_db(conn_app.app)
    config_auth_mode(conn_app.app)

    return conn_app
