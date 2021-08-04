"""This module provides functions to access resources shared across the
Connexion app."""

from flask import current_app, g

from graph_asset_inventory_api.inventory.client import InventoryClient


def get_inventory_client():
    """Returns a new ``InventoryClient``."""
    if 'inventory_client' not in g:
        endpoint = current_app.config['GREMLIN_ENDPOINT']
        auth_mode = current_app.config['GREMLIN_AUTH_MODE']
        current_app.logger.debug(
            f'Creating Inventory Client: {endpoint}, Auth mode: {auth_mode}')
        # pylint: disable=assigning-non-slot
        g.inventory_client = InventoryClient(endpoint, auth_mode)
    return g.inventory_client


def close_inventory_client(_err=None):
    """Closes the ``InventoryClient`` in use."""
    inventory_client = g.pop('inventory_client', None)
    if inventory_client is not None:
        current_app.logger.debug('Closing Inventory Client')
        inventory_client.close()
