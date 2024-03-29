"""Tests for the Asset Inventory API."""

import json
import urllib.parse
from datetime import datetime

from helpers import compare_unsorted_list

from graph_asset_inventory_api.inventory import AssetID
from graph_asset_inventory_api.api import AssetReq


def test_get_assets(flask_cli, init_api_assets):
    """Tests the API endpoint ``GET /v1/assets``."""
    resp = flask_cli.get('/v1/assets')

    assert resp.status_code == 200

    data = json.loads(resp.data)
    assert compare_unsorted_list(data, init_api_assets, lambda x: x['id'])


def test_get_assets_pagination(flask_cli, init_api_assets):
    """Tests the API endpoint ``GET /v1/assets`` with pagination."""
    resp = flask_cli.get('/v1/assets?page=1&size=2')

    assert resp.status_code == 200

    data = json.loads(resp.data)
    assert compare_unsorted_list(data, init_api_assets[2:4], lambda x: x['id'])


def test_get_assets_pagination_missing_size(flask_cli, init_api_assets):
    """Tests the API endpoint ``GET /v1/assets`` with pagination when the size
    parameter is not specified."""
    resp = flask_cli.get('/v1/assets?page=0')

    assert resp.status_code == 200

    data = json.loads(resp.data)
    assert compare_unsorted_list(data, init_api_assets, lambda x: x['id'])


def test_get_assets_by_type(flask_cli, init_api_assets):
    """Tests the API endpoint ``GET /v1/assets`` filtering by a concrete asset
    type."""
    resp = flask_cli.get('/v1/assets?asset_type=type1')

    assert resp.status_code == 200

    data = json.loads(resp.data)
    expected = [
        asset for asset in init_api_assets if asset['type'] == 'type1'
    ]
    assert compare_unsorted_list(data, expected, lambda x: x['id'])


def test_get_assets_by_identifier(flask_cli, init_api_assets):
    """Tests the API endpoint ``GET /v1/assets`` filtering by a concrete asset
    identifier."""
    resp = flask_cli.get('/v1/assets?asset_identifier=identifier1')

    assert resp.status_code == 200

    data = json.loads(resp.data)
    expected = [
        asset for asset in init_api_assets
        if asset['identifier'] == 'identifier1'
    ]
    assert compare_unsorted_list(data, expected, lambda x: x['id'])


def test_get_assets_by_type_identifier(flask_cli, init_api_assets):
    """Tests the API endpoint ``GET /v1/assets`` filtering by a concrete asset
    type and identifier."""
    resp = flask_cli.get(
        '/v1/assets?asset_type=type1&asset_identifier=identifier1',
    )

    assert resp.status_code == 200

    data = json.loads(resp.data)
    expected = [
        asset for asset in init_api_assets
        if asset['type'] == 'type1' and asset['identifier'] == 'identifier1'
    ]
    assert compare_unsorted_list(data, expected, lambda x: x['id'])


def test_get_assets_by_valid_at(flask_cli, init_valid_at_api_assets):
    """Tests the API endpoint ``GET /v1/assets`` filtering by a concrete
    ``valid_at`` time."""
    valid_at = '2010-07-04T01:00:00+00:00'
    valid_at_q = urllib.parse.quote_plus(valid_at)
    valid_at_dt = datetime.fromisoformat(valid_at)

    resp = flask_cli.get(f'/v1/assets?valid_at={valid_at_q}')

    assert resp.status_code == 200

    data = json.loads(resp.data)
    expected = [
        asset for asset in init_valid_at_api_assets
        if (datetime.fromisoformat(asset['first_seen'])
            <= valid_at_dt <=
            datetime.fromisoformat(asset['expiration']))
    ]
    assert compare_unsorted_list(data, expected, lambda x: x['id'])


def test_post_assets(flask_cli, init_api_assets):
    """Tests the API endpoint ``POST /v1/assets``."""
    asset_id = AssetID('new_type', 'new_identifier')

    timestamp = datetime.fromisoformat('2021-07-01T01:00:00+00:00')
    expiration = datetime.fromisoformat('2021-07-07T01:00:00+00:00')

    asset_req = AssetReq(asset_id, timestamp, expiration)

    resp = flask_cli.post(
        '/v1/assets',
        data=json.dumps(asset_req.__dict__),
        content_type='application/json',
    )

    assert resp.status_code == 201

    created_asset = json.loads(resp.data)
    assert created_asset['id'] is not None
    assert created_asset['type'] == asset_req.type
    assert created_asset['identifier'] == asset_req.identifier
    assert created_asset['first_seen'] == timestamp.isoformat()
    assert created_asset['last_seen'] == timestamp.isoformat()
    assert created_asset['expiration'] == expiration.isoformat()

    final_assets = init_api_assets + [created_asset]
    assert compare_unsorted_list(
        json.loads(flask_cli.get('/v1/assets').data),
        final_assets,
        lambda x: x['id'],
    )


def test_post_assets_conflict_error(flask_cli, init_api_assets):
    """Tests the API endpoint ``POST /v1/assets`` with an already existing
    asset ID."""
    asset_id = AssetID(
        init_api_assets[2]['type'], init_api_assets[2]['identifier'])

    timestamp = datetime.fromisoformat('2024-07-01T01:00:00+00:00')
    expiration = datetime.fromisoformat('2024-07-07T01:00:00+00:00')

    asset_req = AssetReq(asset_id, timestamp, expiration)

    resp = flask_cli.post(
        '/v1/assets',
        data=json.dumps(asset_req.__dict__),
        content_type='application/json',
    )

    assert resp.status_code == 409

    assert compare_unsorted_list(
        json.loads(flask_cli.get('/v1/assets').data),
        init_api_assets,
        lambda x: x['id'],
    )


def test_post_assets_empty_type_identifier(flask_cli, init_api_assets):
    """Tests the API endpoint ``POST /v1/assets`` with an empty type or
    identifier string."""
    timestamp = datetime.fromisoformat('2024-07-01T01:00:00+00:00')
    expiration = datetime.fromisoformat('2024-07-07T01:00:00+00:00')

    # Empty type.
    asset_req = AssetReq(
        AssetID('', init_api_assets[2]['identifier']), timestamp, expiration)
    resp = flask_cli.post(
        '/v1/assets',
        data=json.dumps(asset_req.__dict__),
        content_type='application/json',
    )

    assert resp.status_code == 400

    assert compare_unsorted_list(
        json.loads(flask_cli.get('/v1/assets').data),
        init_api_assets,
        lambda x: x['id'],
    )

    # Empty identifier.
    asset_req = AssetReq(
        AssetID(init_api_assets[2]['type'], ''), timestamp, expiration)
    resp = flask_cli.post(
        '/v1/assets',
        data=json.dumps(asset_req.__dict__),
        content_type='application/json',
    )

    assert resp.status_code == 400

    assert compare_unsorted_list(
        json.loads(flask_cli.get('/v1/assets').data),
        init_api_assets,
        lambda x: x['id'],
    )


def test_get_assets_id(flask_cli, init_api_assets):
    """Tests the API endpoint ``GET /v1/assets/{id}``."""
    asset_id = init_api_assets[2]['id']
    resp = flask_cli.get(f'/v1/assets/{asset_id}')
    data = json.loads(resp.data)
    assert data == init_api_assets[2]


def test_get_assets_id_not_found_error(flask_cli):
    """Tests the API endpoint ``GET /v1/assets/{id} with an unknown id."""
    resp = flask_cli.get('/v1/assets/13371337')

    assert resp.status_code == 404


def test_delete_assets_id(flask_cli, init_api_assets):
    """Tests the API endpoint ``DELETE /v1/assets/{id}``."""
    asset_id = init_api_assets[2]['id']
    resp = flask_cli.delete(f'/v1/assets/{asset_id}')

    assert resp.status_code == 204

    final_assets = init_api_assets[:2] + init_api_assets[3:]
    assert compare_unsorted_list(
        json.loads(flask_cli.get('/v1/assets').data),
        final_assets,
        lambda x: x['id'],
    )


def test_delete_assets_id_not_found_error(flask_cli, init_api_assets):
    """Tests the API endpoint ``DELETE /v1/assets/{id}`` with an unknown id."""
    resp = flask_cli.delete('/v1/assets/13371337')

    assert resp.status_code == 404

    assert compare_unsorted_list(
        json.loads(flask_cli.get('/v1/assets').data),
        init_api_assets,
        lambda x: x['id'],
    )


def test_put_assets(flask_cli, init_api_assets):
    """Tests the API endpoint ``PUT /v1/assets``."""
    id_ = init_api_assets[2]['id']

    asset_id = AssetID(
        init_api_assets[2]['type'], init_api_assets[2]['identifier'])

    timestamp = datetime.fromisoformat('2024-07-01T01:00:00+00:00')
    expiration = datetime.fromisoformat('2024-07-07T01:00:00+00:00')

    asset_req = AssetReq(asset_id, timestamp, expiration)

    resp = flask_cli.put(
        f'/v1/assets/{id_}',
        data=json.dumps(asset_req.__dict__),
        content_type='application/json',
    )

    assert resp.status_code == 200

    updated_asset = json.loads(resp.data)
    assert updated_asset['id'] == id_
    assert updated_asset['type'] == asset_req.type
    assert updated_asset['identifier'] == asset_req.identifier
    assert updated_asset['first_seen'] == init_api_assets[2]['first_seen']
    assert updated_asset['last_seen'] == timestamp.isoformat()
    assert updated_asset['expiration'] == expiration.isoformat()

    final_assets = init_api_assets[:2] + init_api_assets[3:] + [updated_asset]
    assert compare_unsorted_list(
        json.loads(flask_cli.get('/v1/assets').data),
        final_assets,
        lambda x: x['id'],
    )


def test_put_assets_id_not_found_error(flask_cli, init_api_assets):
    """Tests the API endpoint ``PUT /v1/assets`` with an unknown ID."""
    asset_id = AssetID(
        init_api_assets[2]['type'], init_api_assets[2]['identifier'])

    timestamp = datetime.fromisoformat('2024-07-01T01:00:00+00:00')
    expiration = datetime.fromisoformat('2024-07-07T01:00:00+00:00')

    asset_req = AssetReq(asset_id, timestamp, expiration)

    resp = flask_cli.put(
        '/v1/assets/31337',
        data=json.dumps(asset_req.__dict__),
        content_type='application/json',
    )

    assert resp.status_code == 404

    assert compare_unsorted_list(
        json.loads(flask_cli.get('/v1/assets').data),
        init_api_assets,
        lambda x: x['id'],
    )


def test_put_assets_asset_id_not_found_error(flask_cli, init_api_assets):
    """Tests the API endpoint ``PUT /v1/assets`` with an unknown ID."""
    id_ = init_api_assets[2]['id']

    asset_id = AssetID(init_api_assets[2]['type'], 'identifier1337')

    timestamp = datetime.fromisoformat('2024-07-01T01:00:00+00:00')
    expiration = datetime.fromisoformat('2024-07-07T01:00:00+00:00')

    asset_req = AssetReq(asset_id, timestamp, expiration)

    resp = flask_cli.put(
        f'/v1/assets/{id_}',
        data=json.dumps(asset_req.__dict__),
        content_type='application/json',
    )

    assert resp.status_code == 404

    assert compare_unsorted_list(
        json.loads(flask_cli.get('/v1/assets').data),
        init_api_assets,
        lambda x: x['id'],
    )


def test_get_assets_encoding(flask_cli):
    """Tests the API endpoint ``GET /v1/assets`` when the query string is URL
    encoded."""

    asset_id = AssetID(
        'http://example.com/aaa?x=x&asset_type=bbb&asset_identifier=ccc',
        'http://example.com/ddd?x=x&asset_type=eee&asset_identifier=fff',
    )

    timestamp = datetime.fromisoformat('2021-07-01T01:00:00+00:00')
    expiration = datetime.fromisoformat('2021-07-07T01:00:00+00:00')

    asset_req = AssetReq(asset_id, timestamp, expiration)

    resp = flask_cli.post(
        '/v1/assets',
        data=json.dumps(asset_req.__dict__),
        content_type='application/json',
    )

    assert resp.status_code == 201

    # Non-urlencoded query string.
    resp = flask_cli.get(
        f'/v1/assets'
        f'?asset_type={asset_id.type}&asset_identifier={asset_id.identifier}'
    )

    assert resp.status_code == 200

    data = json.loads(resp.data)

    assert len(data) == 0

    # Urlencoded query string.
    type_q = urllib.parse.quote_plus(asset_id.type)
    identifier_q = urllib.parse.quote_plus(asset_id.identifier)
    resp = flask_cli.get(
        f'/v1/assets?asset_type={type_q}&asset_identifier={identifier_q}'
    )

    assert resp.status_code == 200

    data = json.loads(resp.data)

    assert len(data) == 1
    assert data[0]['type'] == asset_id.type
    assert data[0]['identifier'] == asset_id.identifier
