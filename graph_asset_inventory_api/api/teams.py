from graph_asset_inventory_api.inventory.foo import foo


def get_teams():
    ret = foo()
    return f'the result of foo() is {ret}'
