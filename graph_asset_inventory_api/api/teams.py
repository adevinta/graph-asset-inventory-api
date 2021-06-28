from flask import (
    make_response,
    jsonify,
)

from graph_asset_inventory_api.context import get_inventory_client
from graph_asset_inventory_api.inventory.types import NotFoundException
from graph_asset_inventory_api.api.types import TeamResp


def get_teams(page=None, size=None):
    cli = get_inventory_client()
    teams = None
    if not page or not size:
        teams = cli.teams()
    else:
        teams = cli.teams_page(page, size)
    resp = [TeamResp.from_dbteam(t).__dict__ for t in teams]
    return make_response(jsonify(resp), 200)


def get_teams_id(id):  # pylint: disable=redefined-builtin
    cli = get_inventory_client()

    team = None
    try:
        team = cli.team(id)
    except NotFoundException:
        return make_response('', 404)

    resp = TeamResp.from_dbteam(team).__dict__
    return make_response(jsonify(resp), 200)
