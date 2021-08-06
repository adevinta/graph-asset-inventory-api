"""Common tests for the Asset Inventory API."""

import json


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
