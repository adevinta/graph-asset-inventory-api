"""Tests for the Asset Inventory API."""

import json
from datetime import datetime

from graph_asset_inventory_api.inventory import AssetID


# pylint: disable=too-many-locals
def test_post_assets_bulk(flask_cli, cli):
    """Tests the API endpoint ``POST /v1/assets/bulk``."""

    # Test the creation of new assets and ``parent_of`` relationships.

    bulk_req_create = {
        'assets': [
            {
                'type': 'type0',
                'identifier': 'identifier0',
                'expiration': '2021-07-07T01:00:00+00:00',
                'timestamp': '2021-07-01T01:00:00+00:00',
                'parents': [
                    {
                        'type': 'type1',
                        'identifier': 'identifier1',
                        'expiration': '2021-07-17T01:00:00+00:00',
                        'timestamp': '2021-07-11T01:00:00+00:00',
                    },
                    {
                        'type': 'type2',
                        'identifier': 'identifier2',
                        'expiration': '2021-07-17T01:00:00+00:00',
                        'timestamp': '2021-07-11T01:00:00+00:00',
                    },
                ],
            },
            {
                'type': 'type1',
                'identifier': 'identifier1',
                'expiration': '2021-07-07T01:00:00+00:00',
                'timestamp': '2021-07-01T01:00:00+00:00',
                'parents': [
                    {
                        'type': 'type2',
                        'identifier': 'identifier2',
                        'expiration': '2021-07-17T01:00:00+00:00',
                        'timestamp': '2021-07-11T01:00:00+00:00',
                    },
                ],
            },
            {
                'type': 'type2',
                'identifier': 'identifier2',
                'expiration': '2021-07-07T01:00:00+00:00',
                'timestamp': '2021-07-01T01:00:00+00:00',
            },
        ],
    }

    resp = flask_cli.post(
        '/v1/assets/bulk',
        data=json.dumps(bulk_req_create),
        content_type='application/json',
    )
    assert resp.status_code == 204

    assets = cli.assets()
    assert len(bulk_req_create['assets']) == len(assets)

    for asset_req in bulk_req_create['assets']:
        asset = cli.asset_id(
            AssetID(asset_req['type'], asset_req['identifier']))
        assert asset.time_attr.first_seen == \
            datetime.fromisoformat(asset_req['timestamp'])
        assert asset.time_attr.last_seen == \
            datetime.fromisoformat(asset_req['timestamp'])
        assert asset.time_attr.expiration == \
            datetime.fromisoformat(asset_req['expiration'])

        parents = cli.parents(asset.vid)

        if 'parents' not in asset_req:
            assert len(parents) == 0
            continue

        assert len(parents) == len(asset_req['parents'])

        for parent_req in asset_req['parents']:
            parent_vid = cli.asset_id(
                AssetID(parent_req['type'], parent_req['identifier']))

            for parent in parents:
                if parent.parent_vid == parent_vid:
                    assert parent.time_attr.first_seen == \
                        datetime.fromisoformat(parent_req['timestamp'])
                    assert parent.time_attr.last_seen == \
                        datetime.fromisoformat(parent_req['timestamp'])
                    assert parent.time_attr.expiration == \
                        datetime.fromisoformat(parent_req['expiration'])
                    break

    # Test the creation and update of assets and ``parent_of`` relationships.

    bulk_req_update = {
        'assets': [
            {
                'type': 'type0',
                'identifier': 'identifier0',
                'expiration': '2022-07-07T01:00:00+00:00',
                'timestamp': '2022-07-01T01:00:00+00:00',
                'parents': [
                    {
                        'type': 'type2',
                        'identifier': 'identifier2',
                        'expiration': '2022-07-17T01:00:00+00:00',
                        'timestamp': '2022-07-11T01:00:00+00:00',
                    },
                    {
                        'type': 'type3',
                        'identifier': 'identifier3',
                        'expiration': '2022-07-17T01:00:00+00:00',
                        'timestamp': '2022-07-11T01:00:00+00:00',
                    },
                ],
            },
            {
                'type': 'type3',
                'identifier': 'identifier3',
                'expiration': '2022-07-07T01:00:00+00:00',
                'timestamp': '2022-07-01T01:00:00+00:00',
            },
        ],
    }

    resp = flask_cli.post(
        '/v1/assets/bulk',
        data=json.dumps(bulk_req_update),
        content_type='application/json',
    )
    assert resp.status_code == 204

    # The number of assets should've been incremented in 1 (from 3 to 4).
    assets = cli.assets()
    assert len(assets) == 4

    # Only ``last_seen`` and ``expiration`` should've been updated because the
    # new dates are in the future.
    asset0 = cli.asset_id(AssetID('type0', 'identifier0'))
    assert asset0.time_attr.first_seen == \
        datetime.fromisoformat('2021-07-01T01:00:00+00:00')
    assert asset0.time_attr.last_seen == \
        datetime.fromisoformat('2022-07-01T01:00:00+00:00')
    assert asset0.time_attr.expiration == \
        datetime.fromisoformat('2022-07-07T01:00:00+00:00')

    # The number of ``parent_of`` relationships for ``type0-identifier0``
    # should've been incremented in 1 (from 2 to 3).
    parents_asset0 = cli.parents(asset0.vid)
    assert len(parents_asset0) == 3

    asset2 = cli.asset_id(AssetID('type2', 'identifier2'))
    for parent in parents_asset0:
        # Only ``last_seen`` and ``expiration`` should've been updated because
        # the new dates are in the future.
        if parent.parent_vid == asset2.vid:
            assert parent.time_attr.first_seen == \
                datetime.fromisoformat('2021-07-11T01:00:00+00:00')
            assert parent.time_attr.last_seen == \
                datetime.fromisoformat('2022-07-11T01:00:00+00:00')
            assert parent.time_attr.expiration == \
                datetime.fromisoformat('2022-07-17T01:00:00+00:00')
            break

    # The number of ``parent_of`` relationships for ``type1-identifier1``
    # should be the same (1).
    asset1 = cli.asset_id(AssetID('type1', 'identifier1'))
    parents_asset1 = cli.parents(asset1.vid)
    assert len(parents_asset1) == 1


def test_post_assets_bulk_not_found_error(flask_cli):
    """Tests the API endpoint ``POST /v1/assets/bulk`` with an unknown
    asset."""

    bulk_req_create = {
        'assets': [
            {
                'type': 'type0',
                'identifier': 'identifier0',
                'expiration': '2021-07-07T01:00:00+00:00',
                'timestamp': '2021-07-01T01:00:00+00:00',
                'parents': [
                    {
                        'type': 'type1337',
                        'identifier': 'identifier1337',
                        'expiration': '2021-07-17T01:00:00+00:00',
                        'timestamp': '2021-07-11T01:00:00+00:00',
                    },
                ],
            },
        ],
    }

    resp = flask_cli.post(
        '/v1/assets/bulk',
        data=json.dumps(bulk_req_create),
        content_type='application/json',
    )
    assert resp.status_code == 404


def test_post_assets_bulk_bad_request_error(flask_cli):
    """Tests the API endpoint ``POST /v1/assets/bulk`` with malformed time
    attributes."""

    bulk_req_create = {
        'assets': [
            {
                'type': 'type0',
                'identifier': 'identifier0',
                'expiration': '2021-07-01T01:00:00+00:00',
                'timestamp': '2021-07-07T01:00:00+00:00',
            },
        ],
    }

    resp = flask_cli.post(
        '/v1/assets/bulk',
        data=json.dumps(bulk_req_create),
        content_type='application/json',
    )
    assert resp.status_code == 400
