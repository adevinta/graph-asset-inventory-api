"""This module implements the request handlers for the endpoints of the Asset
Inventory API related to asset operations."""

import dateutil.parser

import connexion.problem

from graph_asset_inventory_api.context import get_inventory_client
from graph_asset_inventory_api.inventory import (
    Asset,
    AssetID,
    NotFoundError,
    ConflictError,
)
from graph_asset_inventory_api.api import AssetResp


def get_assets(page=None, size=100):
    """Request handler for the API endpoint ``GET /v1/assets``."""
    cli = get_inventory_client()

    assets = cli.assets(page, size)

    resp = [AssetResp.from_dbasset(t).__dict__ for t in assets]
    return resp, 200


def post_assets(body):
    """Request handler for the API endpoint ``POST /v1/assets``."""
    cli = get_inventory_client()

    asset = Asset(AssetID(body['type'], body['identifier']))
    expiration = dateutil.parser.isoparse(body['expiration'])
    timestamp = None
    if 'timestamp' in body:
        timestamp = dateutil.parser.isoparse(body['timestamp'])

    created_asset = None
    try:
        created_asset = cli.add_asset(asset, expiration, timestamp)
    except ConflictError:
        return connexion.problem(409, 'Conflict', 'Asset already exists')
    except ValueError:
        return connexion.problem(400, 'Bad Request', 'Invalid asset ID')

    resp = AssetResp.from_dbasset(created_asset).__dict__
    return resp, 201


def get_assets_id(id):  # pylint: disable=redefined-builtin
    """Request handler for the API endpoint ``GET /v1/assets/{id}``."""
    cli = get_inventory_client()

    asset = None
    try:
        asset = cli.asset(id)
    except NotFoundError:
        return connexion.problem(404, 'Not Found', 'ID not found')

    resp = AssetResp.from_dbasset(asset).__dict__
    return resp, 200


def delete_assets_id(id):  # pylint: disable=redefined-builtin
    """Request handler for the API endpoint ``DELETE /v1/assets/{id}``."""
    cli = get_inventory_client()

    try:
        cli.drop_asset(id)
    except NotFoundError:
        return connexion.problem(404, 'Not Found', 'ID not found')

    return '', 204


def put_assets_id(id, body):  # pylint: disable=redefined-builtin
    """Request handler for the API endpoint ``PUT /v1/assets/{id}``."""
    cli = get_inventory_client()

    asset = Asset(AssetID(body['type'], body['identifier']))
    expiration = dateutil.parser.isoparse(body['expiration'])
    timestamp = None
    if 'timestamp' in body:
        timestamp = dateutil.parser.isoparse(body['timestamp'])

    updated_asset = None
    try:
        updated_asset = cli.update_asset(id, asset, expiration, timestamp)
    except NotFoundError:
        return connexion.problem(404, 'Not Found', 'ID not found')

    resp = AssetResp.from_dbasset(updated_asset).__dict__
    return resp, 200
