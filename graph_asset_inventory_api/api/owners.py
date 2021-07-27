"""This module implements the request handlers for the endpoints of the Asset
Inventory API related to owners operations."""

import dateutil.parser
import connexion.problem

from graph_asset_inventory_api.context import get_inventory_client
from graph_asset_inventory_api.inventory import (
    Owns,
    NotFoundError,
)
from graph_asset_inventory_api.api import OwnsResp


# pylint: disable=redefined-builtin
def get_assets_id_owners(id, page=None, size=100):
    """Request handler for the API endpoint ``GET /v1/assets/{id}/owners``."""
    cli = get_inventory_client()

    owners = None
    try:
        owners = cli.owners(id, page, size)
    except NotFoundError:
        return connexion.problem(404, 'Not Found', 'ID not found')

    resp = [OwnsResp.from_dbowns(o).__dict__ for o in owners]
    return resp, 200


def put_assets_asset_id_owners_team_id(asset_id, team_id, body):
    """Request handler for the API endpoint
    ``PUT /v1/assets/{asset_id}/owners/{team_id}."""
    cli = get_inventory_client()

    owns = Owns(team_id, asset_id)

    start_time = dateutil.parser.isoparse(body['start_time'])
    end_time = None
    if 'end_time' in body:
        end_time = dateutil.parser.isoparse(body['end_time'])

    updated_owns = None
    exists = None
    try:
        updated_owns, exists = cli.set_owns(owns, start_time, end_time)
    except NotFoundError:
        return connexion.problem(404, 'Not Found', 'ID not found')

    status_code = 200 if exists else 201

    resp = OwnsResp.from_dbowns(updated_owns).__dict__
    return resp, status_code


def delete_assets_asset_id_owners_team_id(asset_id, team_id):
    """Request handler for the API endpoint
    ``DELETE /v1/assets/{asset_id}/owners/{team_id}``."""
    cli = get_inventory_client()

    try:
        for owner in cli.owners(asset_id):
            if owner.team_vid == team_id:
                cli.drop_owns(owner.eid)
                return '', 204
    except NotFoundError:
        pass

    return connexion.problem(404, 'Not Found', 'ID not found')
