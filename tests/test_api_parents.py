"""Tests for the Asset Inventory API."""

import json
from datetime import datetime

from helpers import compare_unsorted_list

from graph_asset_inventory_api.api import ParentOfReq


def test_get_assets_id_parents(flask_cli, init_api_parents):
    """Tests the API endpoint ``GET /v1/assets/{id}/parents``."""

    for child_id, parents in init_api_parents.items():
        resp = flask_cli.get(f'/v1/assets/{child_id}/parents')

        assert resp.status_code == 200

        data = json.loads(resp.data)
        assert compare_unsorted_list(data, parents, lambda x: x['id'])


def test_get_assets_id_parents_pagination(flask_cli, init_api_parents):
    """Tests the API endpoint ``GET /v1/assets/{id}/parents`` with
    pagination."""
    child = list(init_api_parents)[0]
    child_id = init_api_parents[child][0]['child_id']

    resp = flask_cli.get(f'/v1/assets/{child_id}/parents?page=1&size=1')

    assert resp.status_code == 200

    data = json.loads(resp.data)
    assert compare_unsorted_list(
        data, init_api_parents[child][1:2], lambda x: x['id'])


def test_get_assets_id_parents_pagination_missing_size(
    flask_cli,
    init_api_parents,
):
    """Tests the API endpoint ``GET /v1/assets/{id}/parents`` with
    pagination when the size parameter is not specified."""
    child = list(init_api_parents)[0]
    child_id = init_api_parents[child][0]['child_id']

    resp = flask_cli.get(f'/v1/assets/{child_id}/parents?page=0')

    assert resp.status_code == 200

    data = json.loads(resp.data)
    assert compare_unsorted_list(
        data, init_api_parents[child], lambda x: x['id'])


def test_get_assets_id_parents_not_found_error(flask_cli):
    """Tests the API endpoint ``GET /v1/assets/{id}/parents``."""

    resp = flask_cli.get('/v1/assets/13371337/parents')

    assert resp.status_code == 404


def test_put_assets_child_id_parents_parent_id_create(
    flask_cli,
    init_api_parents,
    init_assets,
):
    """Tests the API endpoint
    ``PUT /v1/assets/{child_id}/parents/{parent_id}:`` with a new
    relationship."""
    child = list(init_api_parents)[0]
    child_id = init_api_parents[child][0]['child_id']
    parent_id = init_assets[8].vid

    timestamp = datetime.fromisoformat('2024-07-01T01:00:00+00:00')
    expiration = datetime.fromisoformat('2024-07-07T01:00:00+00:00')

    parent_of_req = ParentOfReq(timestamp, expiration)

    resp = flask_cli.put(
        f'/v1/assets/{child_id}/parents/{parent_id}',
        data=json.dumps(parent_of_req.__dict__),
        content_type='application/json',
    )

    assert resp.status_code == 201

    created_parent_of = json.loads(resp.data)

    assert created_parent_of['id'] is not None
    assert created_parent_of['child_id'] == child_id
    assert created_parent_of['parent_id'] == parent_id
    assert created_parent_of['first_seen'] == '2024-07-01T01:00:00+00:00'
    assert created_parent_of['last_seen'] == '2024-07-01T01:00:00+00:00'
    assert created_parent_of['expiration'] == '2024-07-07T01:00:00+00:00'

    final_api_parents = init_api_parents[child] + [created_parent_of]
    assert compare_unsorted_list(
        json.loads(flask_cli.get(f'/v1/assets/{child_id}/parents').data),
        final_api_parents,
        lambda x: x['id'],
    )


def test_put_assets_child_id_parents_parent_id_update(
    flask_cli,
    init_api_parents,
):
    """Tests the API endpoint
    ``PUT /v1/assets/{child_id}/parents/{parent_id}:`` with an existing
    relationship."""
    child = list(init_api_parents)[0]
    init_parent = init_api_parents[child][1]
    child_id = init_parent['child_id']
    parent_id = init_parent['parent_id']

    timestamp = datetime.fromisoformat('2024-07-01T01:00:00+00:00')
    expiration = datetime.fromisoformat('2024-07-07T01:00:00+00:00')

    parent_of_req = ParentOfReq(timestamp, expiration)

    resp = flask_cli.put(
        f'/v1/assets/{child_id}/parents/{parent_id}',
        data=json.dumps(parent_of_req.__dict__),
        content_type='application/json',
    )

    assert resp.status_code == 200

    updated_parent_of = json.loads(resp.data)

    assert updated_parent_of['id'] == init_parent['id']
    assert updated_parent_of['child_id'] == init_parent['child_id']
    assert updated_parent_of['parent_id'] == init_parent['parent_id']
    assert updated_parent_of['first_seen'] == init_parent['first_seen']
    assert updated_parent_of['last_seen'] == '2024-07-01T01:00:00+00:00'
    assert updated_parent_of['expiration'] == '2024-07-07T01:00:00+00:00'

    final_api_parents = init_api_parents[child][:1] + \
        init_api_parents[child][2:] + [updated_parent_of]
    assert compare_unsorted_list(
        json.loads(flask_cli.get(f'/v1/assets/{child_id}/parents').data),
        final_api_parents,
        lambda x: x['id'],
    )


def test_put_assets_child_id_parents_parent_id_not_found_error(
    flask_cli,
    init_api_parents,
):
    """Tests the API endpoint
    ``PUT /v1/assets/{child_id}/parents/{parent_id}:`` with unknown IDs."""
    child = list(init_api_parents)[0]
    child_id = init_api_parents[child][0]['child_id']
    parent_id = init_api_parents[child][0]['parent_id']

    timestamp = datetime.fromisoformat('2024-07-01T01:00:00+00:00')
    expiration = datetime.fromisoformat('2024-07-07T01:00:00+00:00')

    parent_of_req = ParentOfReq(timestamp, expiration)

    resp = flask_cli.put(
        f'/v1/assets/{child_id}/parents/13371337',
        data=json.dumps(parent_of_req.__dict__),
        content_type='application/json',
    )
    assert resp.status_code == 404

    resp = flask_cli.put(
        f'/v1/assets/13371337/parents/{parent_id}',
        data=json.dumps(parent_of_req.__dict__),
        content_type='application/json',
    )
    assert resp.status_code == 404

    assert compare_unsorted_list(
        json.loads(flask_cli.get(f'/v1/assets/{child_id}/parents').data),
        init_api_parents[child],
        lambda x: x['id'],
    )


def test_delete_assets_id(flask_cli, init_api_parents):
    """Tests the API endpoint
    ``DELETE /v1/assets/{child_id}/parents/{parent_id}``."""
    child = list(init_api_parents)[0]
    init_parent = init_api_parents[child][1]
    child_id = init_parent['child_id']
    parent_id = init_parent['parent_id']

    resp = flask_cli.delete(
        f'/v1/assets/{child_id}/parents/{parent_id}',
        content_type='application/json',
    )
    assert resp.status_code == 204

    final_parents = init_api_parents[child][:1] + init_api_parents[child][2:]
    assert compare_unsorted_list(
        json.loads(flask_cli.get(f'/v1/assets/{child_id}/parents').data),
        final_parents,
        lambda x: x['id'],
    )


def test_delete_assets_id_not_found_error(flask_cli, init_api_parents):
    """Tests the API endpoint
    ``DELETE /v1/assets/{child_id}/parents/{parent_id}`` with unknown IDs."""
    child = list(init_api_parents)[0]
    init_parent = init_api_parents[child][1]
    child_id = init_parent['child_id']
    parent_id = init_parent['parent_id']

    resp = flask_cli.delete(
        f'/v1/assets/{child_id}/parents/13371337',
        content_type='application/json',
    )
    assert resp.status_code == 404

    resp = flask_cli.delete(
        f'/v1/assets/13371337/parents/{parent_id}',
        content_type='application/json',
    )
    assert resp.status_code == 404

    assert compare_unsorted_list(
        json.loads(flask_cli.get(f'/v1/assets/{child_id}/parents').data),
        init_api_parents[child],
        lambda x: x['id'],
    )
