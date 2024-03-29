"""This module implements the request handlers for the endpoints of the Asset
Inventory API related to parents operations."""

import dateutil.parser
import connexion.problem

from graph_asset_inventory_api.context import get_inventory_client
from graph_asset_inventory_api.inventory import (
    ParentOf,
    NotFoundError,
)
from graph_asset_inventory_api.api import ParentOfResp


# pylint: disable=redefined-builtin
def get_assets_id_parents(id, page=None, size=100):
    """Request handler for the API endpoint ``GET /v1/assets/{id}/parents``."""
    cli = get_inventory_client()

    parents = None
    try:
        parents = cli.parents(id, page, size)
    except NotFoundError:
        return connexion.problem(404, 'Not Found', 'ID not found')

    resp = [ParentOfResp.from_dbparentof(p).__dict__ for p in parents]
    return resp, 200


def put_assets_child_id_parents_parent_id(child_id, parent_id, body):
    """Request handler for the API endpoint
    ``PUT /v1/assets/{child_id}/parents/{parent_id}``."""
    cli = get_inventory_client()

    parentof = ParentOf(parent_id, child_id)

    expiration = dateutil.parser.isoparse(body['expiration'])
    timestamp = None
    if 'timestamp' in body:
        timestamp = dateutil.parser.isoparse(body['timestamp'])

    updated_parentof = None
    exists = None
    try:
        updated_parentof, exists = cli.set_parent_of(
            parentof, expiration, timestamp)
    except NotFoundError as e:
        return connexion.problem(404, 'Not Found', f'ID not found: {e.name}')

    status_code = 200 if exists else 201

    resp = ParentOfResp.from_dbparentof(updated_parentof).__dict__
    return resp, status_code


def delete_assets_child_id_parents_parent_id(child_id, parent_id):
    """Request handler for the API endpoint
    ``DELETE /v1/assets/{child_id}/parents/{parent_id}``."""
    cli = get_inventory_client()

    try:
        for parent in cli.parents(child_id):
            if parent.parent_vid == parent_id:
                cli.drop_parent_of(parent.eid)
                return '', 204
    except NotFoundError as e:
        return connexion.problem(404, 'Not Found', f'ID not found: {e.name}')

    return connexion.problem(
        404, 'Not Found', f'parent not found: {parent_id}')


# pylint: disable=redefined-builtin
def get_assets_id_children(id, page=None, size=100):
    """Request handler for the API endpoint ``GET
    /v1/assets/{id}/children``."""
    cli = get_inventory_client()

    children = None
    try:
        children = cli.children(id, page, size)
    except NotFoundError:
        return connexion.problem(404, 'Not Found', 'ID not found')

    resp = [ParentOfResp.from_dbparentof(po).__dict__ for po in children]
    return resp, 200
