"""This module implements the request handler for the assets' bulk insert
endpoint of the Asset Inventory API."""

import dateutil.parser
import connexion.problem

from graph_asset_inventory_api.context import get_inventory_client
from graph_asset_inventory_api.inventory import (
    Asset,
    AssetID,
    ParentOf,
    NotFoundError,
)


class ApiBulkAssetInsert:
    """This class implements the bulk insert functionality for assets."""

    def __init__(self, inventory_client):
        self.cli = inventory_client
        self.cache = {}

    def insert(self, assets_req):
        """Insert assets in bulk mode."""
        self._set_assets(assets_req)

        for asset_req in assets_req:
            if 'parents' not in asset_req:
                continue

            # ``child_id`` must be in the cache, given that all the assets are
            # created or updated in the first pass.
            child_id = AssetID(asset_req['type'], asset_req['identifier'])
            child_vid = self.cache[child_id]

            self._set_parents(child_vid, asset_req['parents'])

    def _set_assets(self, assets_req):
        """Updates the assets in the bulk request. If the asset does not exist,
        it is created. It also updates the internal cache with every
        operation."""
        for asset_req in assets_req:
            asset_id = AssetID(asset_req['type'], asset_req['identifier'])
            asset = Asset(asset_id)

            expiration = dateutil.parser.isoparse(asset_req['expiration'])
            timestamp = None
            if 'timestamp' in asset_req:
                timestamp = dateutil.parser.isoparse(asset_req['timestamp'])

            updated_asset, _ = self.cli.set_asset(asset, expiration, timestamp)
            self.cache[asset_id] = updated_asset.vid

    def _set_parents(self, child_vid, parents_req):
        """Updates the ``parent_of`` relationships in the bulk request. If the
        relationship does not exist, it is created. It also updates the
        internal cache with every operation."""
        for parent_req in parents_req:
            parent_id = AssetID(parent_req['type'], parent_req['identifier'])
            parent_vid = self._get_asset_vid(parent_id)

            parentof = ParentOf(parent_vid, child_vid)

            expiration = dateutil.parser.isoparse(parent_req['expiration'])
            timestamp = None
            if 'timestamp' in parent_req:
                timestamp = dateutil.parser.isoparse(parent_req['timestamp'])

            self.cli.set_parent_of(parentof, expiration, timestamp)

    def _get_asset_vid(self, asset_id):
        """Returns the ``vid`` corresponding to the passed ``asset_id``. First,
        it tries to retrieve it from the cache. If it is not found, a DB query
        is executed."""
        if asset_id in self.cache:
            return self.cache[asset_id]

        parent = self.cli.asset_id(asset_id)
        self.cache[asset_id] = parent.vid
        return parent.vid


def post_assets_bulk(body):
    """Request handler for the API endpoint ``GET /v1/assets/bulk``."""

    cli = get_inventory_client()

    try:
        ApiBulkAssetInsert(cli).insert(body['assets'])
    except NotFoundError as e:
        return connexion.problem(404, 'Not Found', f'not found: {e.name}')
    except ValueError as e:
        return connexion.problem(400, 'Bad Request', str(e))

    return '', 204
