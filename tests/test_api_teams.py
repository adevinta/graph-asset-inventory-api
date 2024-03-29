"""Tests for the Asset Inventory API."""

import json
import urllib.parse

from helpers import compare_unsorted_list

from graph_asset_inventory_api.api import TeamReq


def test_get_teams(flask_cli, init_api_teams):
    """Tests the API endpoint ``GET /v1/teams``."""
    resp = flask_cli.get('/v1/teams')
    data = json.loads(resp.data)
    assert compare_unsorted_list(
        data, init_api_teams, lambda x: x['id'])


def test_get_teams_pagination(flask_cli, init_api_teams):
    """Tests the API endpoint ``GET /v1/teams`` with pagination."""
    resp = flask_cli.get('/v1/teams?page=1&size=2')
    data = json.loads(resp.data)
    assert compare_unsorted_list(
        data, init_api_teams[2:4], lambda x: x['id'])


def test_get_teams_pagination_missing_size(flask_cli, init_api_teams):
    """Tests the API endpoint ``GET /v1/teams`` with pagination when the size
    parameter is not specified."""
    resp = flask_cli.get('/v1/teams?page=0')
    data = json.loads(resp.data)
    assert compare_unsorted_list(data, init_api_teams, lambda x: x['id'])


def test_get_teams_by_identifier(flask_cli, init_api_teams):
    """Tests the API endpoint ``GET /v1/teams`` filtering by a concrete team
    identifier."""
    resp = flask_cli.get('/v1/teams?team_identifier=identifier1')

    assert resp.status_code == 200

    data = json.loads(resp.data)
    expected = [
        team for team in init_api_teams if team['identifier'] == 'identifier1'
    ]
    assert compare_unsorted_list(data, expected, lambda x: x['id'])


def test_get_teams_by_identifier_pagination(flask_cli, init_api_teams):
    """Tests the API endpoint ``GET /v1/teams`` filtering by a concrete team
    identifier with pagination."""
    resp = flask_cli.get('/v1/teams?page=0&size=1&team_identifier=identifier1')

    assert resp.status_code == 200

    data = json.loads(resp.data)
    expected = [
        team for team in init_api_teams if team['identifier'] == 'identifier1'
    ]
    expected = expected[:1]
    assert compare_unsorted_list(data, expected, lambda x: x['id'])


def test_post_teams(flask_cli, init_api_teams):
    """Tests the API endpoint ``POST /v1/teams``."""
    team_req = TeamReq('new_identifier', 'new_name')

    resp = flask_cli.post(
        '/v1/teams',
        data=json.dumps(team_req.__dict__),
        content_type='application/json',
    )

    assert resp.status_code == 201

    created_team = json.loads(resp.data)
    assert created_team['id'] is not None
    assert created_team['identifier'] == team_req.identifier
    assert created_team['name'] == team_req.name

    final_teams = init_api_teams + [created_team]
    assert compare_unsorted_list(
        json.loads(flask_cli.get('/v1/teams').data),
        final_teams,
        lambda x: x['id'],
    )


def test_post_teams_conflict_error(flask_cli, init_api_teams):
    """Tests the API endpoint ``POST /v1/teams`` with an already existing
    identifier."""
    team_req = TeamReq(init_api_teams[2]['identifier'], 'new_name')

    resp = flask_cli.post(
        '/v1/teams',
        data=json.dumps(team_req.__dict__),
        content_type='application/json',
    )

    assert resp.status_code == 409

    assert compare_unsorted_list(
        json.loads(flask_cli.get('/v1/teams').data),
        init_api_teams,
        lambda x: x['id'],
    )


def test_post_teams_empty_identifier_name(flask_cli, init_api_teams):
    """Tests the API endpoint ``POST /v1/teams`` with an empty identifier or
    name string."""

    # Empty identifier.
    team_req = TeamReq('', 'new_name')
    resp = flask_cli.post(
        '/v1/teams',
        data=json.dumps(team_req.__dict__),
        content_type='application/json',
    )

    assert resp.status_code == 400

    assert compare_unsorted_list(
        json.loads(flask_cli.get('/v1/teams').data),
        init_api_teams,
        lambda x: x['id'],
    )

    # Empty name.
    team_req = TeamReq('new_identifier', '')
    resp = flask_cli.post(
        '/v1/teams',
        data=json.dumps(team_req.__dict__),
        content_type='application/json',
    )

    assert resp.status_code == 400

    assert compare_unsorted_list(
        json.loads(flask_cli.get('/v1/teams').data),
        init_api_teams,
        lambda x: x['id'],
    )


def test_get_teams_id(flask_cli, init_api_teams):
    """Tests the API endpoint ``GET /v1/teams/{id}``."""
    team_id = init_api_teams[2]['id']
    resp = flask_cli.get(f'/v1/teams/{team_id}')
    data = json.loads(resp.data)
    assert data == init_api_teams[2]


def test_get_teams_id_not_found_error(flask_cli):
    """Tests the API endpoint ``GET /v1/teams/{id} with an unknown id."""
    resp = flask_cli.get('/v1/teams/13371337')

    assert resp.status_code == 404


def test_delete_teams_id(flask_cli, init_api_teams):
    """Tests the API endpoint ``DELETE /v1/teams/{id}``."""
    team_id = init_api_teams[2]['id']
    resp = flask_cli.delete(f'/v1/teams/{team_id}')

    assert resp.status_code == 204

    final_teams = init_api_teams[:2] + init_api_teams[3:]
    assert compare_unsorted_list(
        json.loads(flask_cli.get('/v1/teams').data),
        final_teams,
        lambda x: x['id'],
    )


def test_delete_teams_id_not_found_error(flask_cli, init_api_teams):
    """Tests the API endpoint ``DELETE /v1/teams/{id}`` with an unknown id."""
    resp = flask_cli.delete('/v1/teams/13371337')

    assert resp.status_code == 404

    assert compare_unsorted_list(
        json.loads(flask_cli.get('/v1/teams').data),
        init_api_teams,
        lambda x: x['id'],
    )


def test_put_teams(flask_cli, init_api_teams):
    """Tests the API endpoint ``PUT /v1/teams``."""
    team_id = init_api_teams[2]['id']
    team_req = TeamReq(init_api_teams[2]['identifier'], 'new_name')

    resp = flask_cli.put(
        f'/v1/teams/{team_id}',
        data=json.dumps(team_req.__dict__),
        content_type='application/json',
    )

    assert resp.status_code == 200

    updated_team = json.loads(resp.data)
    assert updated_team['id'] == team_id
    assert updated_team['identifier'] == team_req.identifier
    assert updated_team['name'] == team_req.name

    final_teams = init_api_teams[:2] + init_api_teams[3:] + [updated_team]
    assert compare_unsorted_list(
        json.loads(flask_cli.get('/v1/teams').data),
        final_teams,
        lambda x: x['id'],
    )


def test_put_teams_id_not_found_error(flask_cli, init_api_teams):
    """Tests the API endpoint ``PUT /v1/teams`` with an unknown id."""
    team_req = TeamReq(
        init_api_teams[2]['identifier'], init_api_teams[2]['name'])

    resp = flask_cli.put(
        '/v1/teams/31337',
        data=json.dumps(team_req.__dict__),
        content_type='application/json',
    )

    assert resp.status_code == 404

    assert compare_unsorted_list(
        json.loads(flask_cli.get('/v1/teams').data),
        init_api_teams,
        lambda x: x['id'],
    )


def test_put_teams_identifier_not_found_error(flask_cli, init_api_teams):
    """Tests the API endpoint ``PUT /v1/teams`` with an unknown identifier."""
    team_id = init_api_teams[2]['id']
    team_req = TeamReq('identifier1337', init_api_teams[2]['name'])

    resp = flask_cli.put(
        f'/v1/teams/{team_id}',
        data=json.dumps(team_req.__dict__),
        content_type='application/json',
    )

    assert resp.status_code == 404

    assert compare_unsorted_list(
        json.loads(flask_cli.get('/v1/teams').data),
        init_api_teams,
        lambda x: x['id'],
    )


def test_get_teams_encoding(flask_cli):
    """Tests the API endpoint ``GET /v1/teams`` when the query string is URL
    encoded."""

    team_req = TeamReq(
        'http://example.com/aaa?x=x&team_identifier=bbb',
        'http://example.com/ccc?x=x&team_identifier=ddd',
    )

    resp = flask_cli.post(
        '/v1/teams',
        data=json.dumps(team_req.__dict__),
        content_type='application/json',
    )

    assert resp.status_code == 201

    # Non-urlencoded query string.
    resp = flask_cli.get(f'/v1/teams?team_identifier={team_req.identifier}')

    assert resp.status_code == 200

    data = json.loads(resp.data)

    assert len(data) == 0

    # Urlencoded query string.
    identifier_q = urllib.parse.quote_plus(team_req.identifier)
    resp = flask_cli.get(f'/v1/teams?team_identifier={identifier_q}')

    assert resp.status_code == 200

    data = json.loads(resp.data)

    assert len(data) == 1
    assert data[0]['identifier'] == team_req.identifier
    assert data[0]['name'] == team_req.name
