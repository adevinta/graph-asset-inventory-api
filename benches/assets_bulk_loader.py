#!/usr/bin/env python3

"""Benchmark bulk assets creation."""

import sys
import csv
import json
import time
from datetime import (
    datetime,
    timezone,
)
from urllib.parse import urljoin

import requests


def process_assets(csv_data):
    """Process assets CSV."""
    fields = [
        'seq',
        'type',
        'identifier',
        'timestamp',
        'expiration',
        'parent_type',
        'parent_identifier',
        'parent_of_timestamp',
        'parent_of_expiration',
    ]

    assets = []
    for record in csv.DictReader(csv_data, fieldnames=fields):
        asset = {
            'type': record['type'],
            'identifier': record['identifier'],
            'timestamp': datetime.fromtimestamp(
                int(record['timestamp']),
                tz=timezone.utc,
            ).isoformat(),
            'expiration': datetime.fromtimestamp(
                int(record['expiration']),
                tz=timezone.utc,
            ).isoformat(),
            'parents': [],
        }

        if record['parent_type'] != '' and record['parent_identifier'] != '':
            parent = {
                'type': record['parent_type'],
                'identifier': record['parent_identifier'],
                'timestamp': datetime.fromtimestamp(
                    int(record['parent_of_timestamp']),
                    tz=timezone.utc,
                ).isoformat(),
                'expiration': datetime.fromtimestamp(
                    int(record['parent_of_expiration']),
                    tz=timezone.utc,
                ).isoformat(),
            }
            asset['parents'].append(parent)

        assets.append(asset)

    return {'assets': assets}


def main():
    """Main function."""
    if len(sys.argv) != 2:
        sys.exit(f'usage: {sys.argv[0]} <url>')
    url = sys.argv[1]

    bulk_endpoint = urljoin(url, '/v1/assets/bulk')

    data = process_assets(sys.stdin.readlines())

    start_time = time.time()
    resp = requests.post(bulk_endpoint, json=data)
    elapsed = time.time() - start_time

    if resp.status_code != 204:
        sys.exit(
            f'error: status_code={resp.status_code} data={resp.text}')

    num_assets = len(data['assets'])

    speed = num_assets / elapsed

    print(f'Sent {num_assets} assets ({len(json.dumps(data)) / 1024:.2f} KB) '
          f'took {elapsed:.2f} seconds ({speed:.0f} assets/s)')


if __name__ == '__main__':
    main()
