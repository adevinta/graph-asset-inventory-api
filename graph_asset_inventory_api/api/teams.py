"""This module implements the request handlers for the endpoints of the Asset
Inventory API related to team operations."""

import connexion.problem

from graph_asset_inventory_api.context import get_inventory_client
from graph_asset_inventory_api.inventory import (
    Team,
    NotFoundError,
    ConflictError,
)
from graph_asset_inventory_api.api import TeamResp


def get_teams(page=None, size=100, team_identifier=None):
    """Request handler for the API endpoint ``GET /v1/teams``."""
    cli = get_inventory_client()

    teams = cli.teams(page, size, team_identifier)

    resp = [TeamResp.from_dbteam(t).__dict__ for t in teams]
    return resp, 200


def post_teams(body):
    """Request handler for the API endpoint ``POST /v1/teams``."""
    cli = get_inventory_client()

    team = Team(body['identifier'], body['name'])

    created_team = None
    try:
        created_team = cli.add_team(team)
    except ConflictError:
        return connexion.problem(409, 'Conflict', 'Team already exists')
    except ValueError as e:
        return connexion.problem(400, 'Bad Request', str(e))

    resp = TeamResp.from_dbteam(created_team).__dict__
    return resp, 201


def get_teams_id(id):  # pylint: disable=redefined-builtin
    """Request handler for the API endpoint ``GET /v1/teams/{id}``."""
    cli = get_inventory_client()

    team = None
    try:
        team = cli.team(id)
    except NotFoundError:
        return connexion.problem(404, 'Not Found', 'ID not found')

    resp = TeamResp.from_dbteam(team).__dict__
    return resp, 200


def delete_teams_id(id):  # pylint: disable=redefined-builtin
    """Request handler for the API endpoint ``DELETE /v1/teams/{id}``."""
    cli = get_inventory_client()

    try:
        cli.drop_team(id)
    except NotFoundError:
        return connexion.problem(404, 'Not Found', 'ID not found')

    return '', 204


def put_teams_id(id, body):  # pylint: disable=redefined-builtin
    """Request handler for the API endpoint ``PUT /v1/teams/{id}``."""
    cli = get_inventory_client()

    team = Team(body['identifier'], body['name'])

    updated_team = None
    try:
        updated_team = cli.update_team(id, team)
    except NotFoundError:
        return connexion.problem(404, 'Not Found', 'ID not found')

    resp = TeamResp.from_dbteam(updated_team).__dict__
    return resp, 200
