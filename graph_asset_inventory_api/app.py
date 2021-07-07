#!/usr/bin/env python3

"""Entry point of the Graph Asset Inventory API."""

import os

from graph_asset_inventory_api.factory import create_app


if __name__ == '__main__':
    port = os.getenv('PORT', '8000')
    create_app().run(port=int(port))
