"""Common tests for the Asset Inventory API."""

import json

from graph_asset_inventory_api.factory import create_app


def test_wrong_gremlin_endpoint():
    """Tests that an HTTP error is returned by the API if the Gremlin endpoint
    is not valid."""
    conn_app = create_app()

    # Do not propagate exceptions. We are checking the returned status code, so
    # the application is the one that should handle the exceptions.
    conn_app.app.testing = False
    conn_app.app.debug = False

    # Set an invalid Gremlin endpoint.
    conn_app.app.config['GREMLIN_ENDPOINT'] = 'ws://invalid-host:8182/gremlin'

    with conn_app.app.test_client() as flask_cli:
        resp = flask_cli.get('/v1/teams')
        assert resp.status_code == 500


def test_datetime_validation(flask_cli):
    """Tests the validation of date-time fields."""

    # Wrong format.

    asset_req = {
        'type': 'type0',
        'identifier': 'identifier0',
        'timestamp': '1234',
        'expiration': '2021-07-07T01:00:00+00:00',
    }

    resp = flask_cli.post(
        '/v1/assets',
        data=json.dumps(asset_req),
        content_type='application/json',
    )

    assert resp.status_code == 400

    # Wrong format with small mistake.

    asset_req['timestamp'] = '2021-07-01T01:000:00+00:00'

    resp = flask_cli.post(
        '/v1/assets',
        data=json.dumps(asset_req),
        content_type='application/json',
    )

    assert resp.status_code == 400

    # Correct format.

    asset_req['timestamp'] = '2021-07-01T01:00:00+00:00'

    resp = flask_cli.post(
        '/v1/assets',
        data=json.dumps(asset_req),
        content_type='application/json',
    )

    assert resp.status_code == 201


def test_datetime_rfc3339_parsing(flask_cli):
    """Tests rfc3339 parsing."""
    asset_req = {
        'type': 'type0',
        'identifier': 'identifier0',
        'timestamp': '2021-07-01T01:00:00Z',
        'expiration': '2021-07-07T03:00:00+02:00',
    }

    resp = flask_cli.post(
        '/v1/assets',
        data=json.dumps(asset_req),
        content_type='application/json',
    )
    resp_data = json.loads(resp.data)

    assert resp.status_code == 201

    assert resp_data['first_seen'] == '2021-07-01T01:00:00+00:00'
    assert resp_data['last_seen'] == '2021-07-01T01:00:00+00:00'
    assert resp_data['expiration'] == '2021-07-07T01:00:00+00:00'


def test_datetime_timezone(flask_cli):
    """Tests if gremlin returns the expected timezone for datetime
    properties."""
    asset_req = {
        'type': 'type0',
        'identifier': 'identifier0',
        'timestamp': '2021-07-01T05:00:00+04:00',
        'expiration': '2021-07-07T01:00:00+00:00',
    }

    resp = flask_cli.post(
        '/v1/assets',
        data=json.dumps(asset_req),
        content_type='application/json',
    )
    resp_data = json.loads(resp.data)

    assert resp.status_code == 201

    assert resp_data['first_seen'] == '2021-07-01T01:00:00+00:00'
    assert resp_data['last_seen'] == '2021-07-01T01:00:00+00:00'
    assert resp_data['expiration'] == '2021-07-07T01:00:00+00:00'
