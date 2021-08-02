"""Tests for the Asset Inventory API."""

import json
from datetime import datetime

from helpers import compare_unsorted_list

from graph_asset_inventory_api.api import OwnsReq
from graph_asset_inventory_api.inventory import TeamTimeAttr


def test_get_assets_id_owners(flask_cli, init_api_owners):
    """Tests the API endpoint ``GET /v1/assets/{id}/owners``."""

    for asset_id, owners in init_api_owners.items():
        resp = flask_cli.get(f'/v1/assets/{asset_id}/owners')

        assert resp.status_code == 200

        data = json.loads(resp.data)
        assert compare_unsorted_list(data, owners, lambda x: x['id'])


def test_get_assets_id_owners_pagination(flask_cli, init_api_owners):
    """Tests the API endpoint ``GET /v1/assets/{id}/owners`` with
    pagination."""
    asset = list(init_api_owners)[0]
    asset_id = init_api_owners[asset][0]['asset_id']

    resp = flask_cli.get(f'/v1/assets/{asset_id}/owners?page=1&size=1')

    assert resp.status_code == 200

    data = json.loads(resp.data)
    assert compare_unsorted_list(
        data, init_api_owners[asset][1:2], lambda x: x['id'])


def test_get_assets_id_owners_pagination_missing_size(
    flask_cli,
    init_api_owners
):
    """Tests the API endpoint ``GET /v1/assets/{id}/owners`` with
    pagination when the size parameter is not specified."""
    asset = list(init_api_owners)[0]
    asset_id = init_api_owners[asset][0]['asset_id']

    resp = flask_cli.get(f'/v1/assets/{asset_id}/owners?page=0')

    assert resp.status_code == 200

    data = json.loads(resp.data)
    assert compare_unsorted_list(
        data, init_api_owners[asset], lambda x: x['id'])


def test_get_assets_id_owners_not_found_error(flask_cli):
    """Tests the API endpoint ``GET /v1/assets/{id}/owners`` with
    an unknown ID."""
    resp = flask_cli.get('/v1/assets/13371337/owners')

    assert resp.status_code == 404


def test_put_assets_asset_id_owners_team_id_create(
    flask_cli,
    init_api_owners,
    init_teams,
):
    """Tests the API endpoint
    ``PUT /v1/assets/{asset_id}/owners/{team_id}`` with a new relationship."""
    asset = list(init_api_owners)[0]
    asset_id = init_api_owners[asset][0]['asset_id']
    team_id = init_teams[4].vid

    start_time = datetime.fromisoformat('2024-07-01T01:00:00+00:00')
    end_time = datetime.fromisoformat('2024-07-07T01:00:00+00:00')

    owns_req = OwnsReq(TeamTimeAttr(start_time, end_time))

    resp = flask_cli.put(
        f'/v1/assets/{asset_id}/owners/{team_id}',
        data=json.dumps(owns_req.__dict__),
        content_type='application/json',
    )

    assert resp.status_code == 201

    created_owns = json.loads(resp.data)

    assert created_owns['id'] is not None
    assert created_owns['asset_id'] == asset_id
    assert created_owns['team_id'] == team_id
    assert created_owns['start_time'] == '2024-07-01T01:00:00+00:00'
    assert created_owns['end_time'] == '2024-07-07T01:00:00+00:00'

    final_api_owners = init_api_owners[asset] + [created_owns]
    assert compare_unsorted_list(
        json.loads(flask_cli.get(f'/v1/assets/{asset_id}/owners').data),
        final_api_owners,
        lambda x: x['id'],
    )


def test_put_assets_asset_id_owners_team_id_create_missing_end_time(
    flask_cli,
    init_api_owners,
    init_teams,
):
    """Tests the API endpoint
    ``PUT /v1/assets/{asset_id}/owners/{team_id}`` with a new relationship."""
    asset = list(init_api_owners)[0]
    asset_id = init_api_owners[asset][0]['asset_id']
    team_id = init_teams[4].vid

    owns_req = {
        'start_time': '2024-07-01T01:00:00+00:00',
    }

    resp = flask_cli.put(
        f'/v1/assets/{asset_id}/owners/{team_id}',
        data=json.dumps(owns_req),
        content_type='application/json',
    )

    assert resp.status_code == 201

    created_owns = json.loads(resp.data)

    assert created_owns['id'] is not None
    assert created_owns['asset_id'] == asset_id
    assert created_owns['team_id'] == team_id
    assert created_owns['start_time'] == '2024-07-01T01:00:00+00:00'
    assert created_owns['end_time'] is None

    final_api_owners = init_api_owners[asset] + [created_owns]
    assert compare_unsorted_list(
        json.loads(flask_cli.get(f'/v1/assets/{asset_id}/owners').data),
        final_api_owners,
        lambda x: x['id'],
    )


def test_put_assets_asset_id_owners_team_id_update(
    flask_cli,
    init_api_owners,
):
    """Tests the API endpoint
    ``PUT /v1/assets/{asset_id}/owners/{team_id}`` with an existing
    relationship."""
    asset = list(init_api_owners)[0]
    init_owner = init_api_owners[asset][1]
    asset_id = init_owner['asset_id']
    team_id = init_owner['team_id']

    start_time = datetime.fromisoformat('2024-07-01T01:00:00+00:00')
    end_time = datetime.fromisoformat('2024-07-07T01:00:00+00:00')

    owns_req = OwnsReq(TeamTimeAttr(start_time, end_time))

    resp = flask_cli.put(
        f'/v1/assets/{asset_id}/owners/{team_id}',
        data=json.dumps(owns_req.__dict__),
        content_type='application/json',
    )

    assert resp.status_code == 200

    created_owns = json.loads(resp.data)

    assert created_owns['id'] == init_owner['id']
    assert created_owns['asset_id'] == asset_id
    assert created_owns['team_id'] == team_id
    assert created_owns['start_time'] == '2024-07-01T01:00:00+00:00'
    assert created_owns['end_time'] == '2024-07-07T01:00:00+00:00'

    final_api_owners = init_api_owners[asset][:1] + \
        init_api_owners[asset][2:] + [created_owns]
    assert compare_unsorted_list(
        json.loads(flask_cli.get(f'/v1/assets/{asset_id}/owners').data),
        final_api_owners,
        lambda x: x['id'],
    )


def test_put_assets_asset_id_owners_team_id_not_found_error(
    flask_cli,
    init_api_owners,
):
    """Tests the API endpoint
    ``PUT /v1/assets/{asset_id}/owners/{team_id}`` with unknowns IDs."""
    asset = list(init_api_owners)[0]
    asset_id = init_api_owners[asset][0]['asset_id']
    team_id = init_api_owners[asset][0]['team_id']

    start_time = datetime.fromisoformat('2024-07-01T01:00:00+00:00')
    end_time = datetime.fromisoformat('2024-07-07T01:00:00+00:00')

    owns_req = OwnsReq(TeamTimeAttr(start_time, end_time))

    resp = flask_cli.put(
        f'/v1/assets/{asset_id}/owners/13371337',
        data=json.dumps(owns_req.__dict__),
        content_type='application/json',
    )
    assert resp.status_code == 404

    resp = flask_cli.put(
        f'/v1/assets/13371337/owners/{team_id}',
        data=json.dumps(owns_req.__dict__),
        content_type='application/json',
    )
    assert resp.status_code == 404

    assert compare_unsorted_list(
        json.loads(flask_cli.get(f'/v1/assets/{asset_id}/owners').data),
        init_api_owners[asset],
        lambda x: x['id'],
    )


def test_delete_assets_asset_id_owners_team_id(
    flask_cli,
    init_api_owners,
):
    """Tests the API endpoint
    ``DELETE /v1/assets/{asset_id}/owners/{team_id}``."""
    asset = list(init_api_owners)[0]
    init_owner = init_api_owners[asset][1]
    asset_id = init_owner['asset_id']
    team_id = init_owner['team_id']

    resp = flask_cli.delete(
        f'/v1/assets/{asset_id}/owners/{team_id}',
        content_type='application/json',
    )
    assert resp.status_code == 204

    final_owners = init_api_owners[asset][:1] + init_api_owners[asset][2:]
    assert compare_unsorted_list(
        json.loads(flask_cli.get(f'/v1/assets/{asset_id}/owners').data),
        final_owners,
        lambda x: x['id'],
    )


def test_delete_assets_asset_id_owners_team_id_not_found_error(
    flask_cli,
    init_api_owners,
):
    """Tests the API endpoint
    ``DELETE /v1/assets/{asset_id}/owners/{team_id}`` with unknowns IDs."""
    asset = list(init_api_owners)[0]
    init_owner = init_api_owners[asset][1]
    asset_id = init_owner['asset_id']
    team_id = init_owner['team_id']

    resp = flask_cli.delete(
        f'/v1/assets/{asset_id}/owners/13371337',
        content_type='application/json',
    )
    assert resp.status_code == 404

    resp = flask_cli.delete(
        f'/v1/assets/13371337/owners/{team_id}',
        content_type='application/json',
    )
    assert resp.status_code == 404

    assert compare_unsorted_list(
        json.loads(flask_cli.get(f'/v1/assets/{asset_id}/owners').data),
        init_api_owners[asset],
        lambda x: x['id'],
    )
