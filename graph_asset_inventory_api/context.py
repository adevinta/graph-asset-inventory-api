from flask import current_app, g

from graph_asset_inventory_api.inventory.client import InventoryClient


def get_inventory_client():
    if 'inventory_client' not in g:
        endpoint = current_app.config['NEPTUNE_ENDPOINT']
        current_app.logger.debug(f'Creating Inventory Client: {endpoint}')
        # pylint: disable=assigning-non-slot
        g.inventory_client = InventoryClient(endpoint)
    return g.inventory_client


def close_inventory_client(_err=None):
    inventory_client = g.pop('inventory_client', None)
    if inventory_client is not None:
        current_app.logger.debug('Closing Inventory Client')
        inventory_client.close()
