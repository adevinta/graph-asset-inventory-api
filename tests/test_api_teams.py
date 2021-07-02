"""Tests for the Asset Inventory API."""

import json

from helpers import compare_unsorted_list


def test_get_teams(flask_cli, init_api_teams):
    """Test API endpoint ``/v1/teams``."""

    resp = flask_cli.get('/v1/teams')
    data = json.loads(resp.data)
    assert compare_unsorted_list(
        data, init_api_teams, lambda x: x['identifier'])


def test_get_teams_page(flask_cli, init_api_teams):
    """Test API endpoint ``/v1/teams`` with pagination."""

    resp = flask_cli.get('/v1/teams?page=1&size=2')
    data = json.loads(resp.data)
    assert compare_unsorted_list(
        data, init_api_teams[2:4], lambda x: x['identifier'])


def test_get_teams_id(flask_cli, init_api_teams):
    """Test API endpoint ``/v1/teams/{id}``."""

    team_id = init_api_teams[2]['id']
    resp = flask_cli.get(f'/v1/teams/{team_id}')
    data = json.loads(resp.data)
    assert data == init_api_teams[2]
