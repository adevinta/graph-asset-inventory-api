"""Tests for the class ``InventoryClient``."""

from datetime import datetime

import pytest

from helpers import compare_unsorted_list

from graph_asset_inventory_api.inventory import (
    AssetID,
    Asset,
    Team,
    ParentOf,
    Owns,
    NotFoundError,
    ConflictError,
)


# Teams.


def test_teams(cli, init_teams):
    """Tests the method ``teams`` of the class ``InventoryClient``."""
    teams = cli.teams()
    assert compare_unsorted_list(teams, init_teams, lambda x: x.vid)


def test_teams_pagination(cli, init_teams):
    """Tests the pagination mode of the method ``teams`` of the class
    ``InventoryClient``."""
    assert compare_unsorted_list(
        cli.teams(1, 2), init_teams[2:4], lambda x: x.vid)
    assert compare_unsorted_list(
        cli.teams(0, 2), init_teams[0:2], lambda x: x.vid)
    assert compare_unsorted_list(
        cli.teams(2, 2), init_teams[4:5], lambda x: x.vid)
    assert compare_unsorted_list(
        cli.teams(1, 1), init_teams[1:2], lambda x: x.vid)
    assert compare_unsorted_list(
        cli.teams(0, 1000), init_teams, lambda x: x.vid)


def test_team(cli, init_teams):
    """Tests the method ``team`` of the class ``InventoryClient``."""
    team = cli.team(init_teams[2].vid)
    assert team == init_teams[2]


def test_team_not_found_error(cli):
    """Tests the method ``team`` of the class ``InventoryClient`` with an
    unknown ``vid``."""
    with pytest.raises(NotFoundError, match=r'.*13371337.*') as exc_info:
        cli.team(13371337)

    assert exc_info.value.name == 13371337


def test_team_identifier(cli, init_teams):
    """Tests the method ``team_identifier`` of the class
    ``InventoryClient``."""
    team = cli.team_identifier(init_teams[2].identifier)
    assert team == init_teams[2]


def test_team_identifier_not_found_error(cli):
    """Tests the method ``team_identifier`` of the class ``InventoryClient``
    with an unknown identifier."""
    with pytest.raises(NotFoundError, match='.*identifier1337.*') as exc_info:
        cli.team_identifier('identifier1337')

    assert exc_info.value.name == 'identifier1337'


def test_add_team(cli, init_teams):
    """Tests the method ``add_team`` of the class ``InventoryClient``."""
    team = Team('identifier_created', 'name_created')
    created_team = cli.add_team(team)

    assert created_team.vid is not None
    assert created_team.identifier == team.identifier
    assert created_team.name == team.name

    final_teams = init_teams + [created_team]
    assert compare_unsorted_list(cli.teams(), final_teams, lambda x: x.vid)


def test_add_team_empty_identifier_name(cli, init_teams):
    """Tests the method ``add_asset`` of the class ``InventoryClient`` with an
    empty identifier or name string."""
    with pytest.raises(ValueError, match='invalid identifier'):
        cli.add_team(Team('', 'new_name'))
    assert compare_unsorted_list(cli.teams(), init_teams, lambda x: x.vid)

    with pytest.raises(ValueError, match='invalid name'):
        cli.add_team(Team('new_identifier', ''))
    assert compare_unsorted_list(cli.teams(), init_teams, lambda x: x.vid)


def test_add_team_conflict_error(cli, init_teams):
    """Tests the method ``add_team`` of the class ``InventoryClient`` with an
    already existing team."""
    identifier = init_teams[2].identifier

    team = Team(identifier, 'new_name')

    with pytest.raises(ConflictError, match=f'.*{identifier}.*') as exc_info:
        cli.add_team(team)

    assert exc_info.value.name == identifier

    assert compare_unsorted_list(cli.teams(), init_teams, lambda x: x.vid)


def test_update_team(cli, init_teams):
    """Tests the method ``update_team`` of the class ``InventoryClient``."""
    team = Team(init_teams[2].identifier, 'name_updated')
    created_team = cli.update_team(init_teams[2].vid, team)

    assert created_team.vid == init_teams[2].vid
    assert created_team.identifier == init_teams[2].identifier
    assert created_team.name == team.name

    final_teams = init_teams[:2] + init_teams[3:] + [created_team]
    assert compare_unsorted_list(cli.teams(), final_teams, lambda x: x.vid)


def test_update_team_vid_not_found_error(cli, init_teams):
    """Tests the method ``update_team`` of the class ``InventoryClient`` with
    an unknown ``vid``."""
    team = Team(init_teams[2].identifier, 'name_updated')

    with pytest.raises(NotFoundError, match='.*13371337.*') as exc_info:
        cli.update_team(13371337, team)

    assert exc_info.value.name == 13371337

    assert compare_unsorted_list(cli.teams(), init_teams, lambda x: x.vid)


def test_update_team_identifier_not_found_error(cli, init_teams):
    """Tests the method ``update_team`` of the class ``InventoryClient`` with
    an unknown ``identifier``."""
    vid = init_teams[2].vid
    team = Team('identifier1337', 'name_updated')

    with pytest.raises(NotFoundError, match=f'.*{vid}.*') as exc_info:
        cli.update_team(vid, team)

    assert exc_info.value.name == vid

    assert compare_unsorted_list(cli.teams(), init_teams, lambda x: x.vid)


def test_drop_team(cli, init_teams):
    """Tests the method ``drop_team`` of the class ``InventoryClient``."""
    cli.drop_team(init_teams[2].vid)

    final_teams = init_teams[:2] + init_teams[3:]
    assert compare_unsorted_list(cli.teams(), final_teams, lambda x: x.vid)


def test_drop_team_not_found_error(cli, init_teams):
    """Tests the method ``drop_team`` of the class ``InventoryClient`` with an
    unknown ``vid``."""
    with pytest.raises(NotFoundError, match='.*13371337.*') as exc_info:
        cli.drop_team(13371337)

    assert exc_info.value.name == 13371337

    assert compare_unsorted_list(cli.teams(), init_teams, lambda x: x.vid)


# Assets.


def test_assets(cli, init_assets):
    """Tests the method ``assets`` of the class ``InventoryClient``."""
    assets = cli.assets()
    assert compare_unsorted_list(assets, init_assets, lambda x: x.vid)


def test_assets_pagination(cli, init_assets):
    """Tests the pagination mode of the method ``assets`` of the class
    ``InventoryClient``."""
    assert compare_unsorted_list(
        cli.assets(1, 2), init_assets[2:4], lambda x: x.vid)
    assert compare_unsorted_list(
        cli.assets(0, 2), init_assets[0:2], lambda x: x.vid)
    assert compare_unsorted_list(
        cli.assets(2, 8), init_assets[9:10], lambda x: x.vid)
    assert compare_unsorted_list(
        cli.assets(1, 1), init_assets[1:2], lambda x: x.vid)
    assert compare_unsorted_list(
        cli.assets(0, 1000), init_assets, lambda x: x.vid)


def test_asset(cli, init_assets):
    """Tests the method ``asset`` of the class ``InventoryClient``."""
    asset = cli.asset(init_assets[2].vid)
    assert asset == init_assets[2]


def test_asset_not_found_error(cli):
    """Tests the method ``asset`` of the class ``InventoryClient`` with an
    unknown ``vid``."""
    with pytest.raises(NotFoundError, match=r'.*13371337.*') as exc_info:
        cli.asset(13371337)

    assert exc_info.value.name == 13371337


def test_asset_identifier(cli, init_assets):
    """Tests the method ``asset_id`` of the class ``InventoryClient``."""
    asset_id = AssetID(
        init_assets[2].asset_id.type, init_assets[2].asset_id.identifier)
    asset = cli.asset_id(asset_id)
    assert asset == init_assets[2]


def test_asset_id_not_found_error(cli):
    """Tests the method ``asset_id`` of the class ``InventoryClient`` with an
    unknown asset ID."""
    asset_id = AssetID('type1337', 'identifier1337')

    with pytest.raises(NotFoundError, match=f'.*{asset_id}.*') as exc_info:
        cli.asset_id(asset_id)

    assert exc_info.value.name == asset_id


def test_drop_asset(cli, init_assets):
    """Tests the method ``drop_asset`` of the class ``InventoryClient``."""
    cli.drop_asset(init_assets[2].vid)

    final_assets = init_assets[:2] + init_assets[3:]
    assert compare_unsorted_list(cli.assets(), final_assets, lambda x: x.vid)


def test_drop_asset_not_found_error(cli, init_assets):
    """Tests the method ``drop_asset`` of the class ``InventoryClient`` with an
    unknown ``vid``."""
    with pytest.raises(NotFoundError, match='.*13371337.*') as exc_info:
        cli.drop_asset(13371337)

    assert exc_info.value.name == 13371337

    assert compare_unsorted_list(cli.assets(), init_assets, lambda x: x.vid)


def test_add_asset(cli, init_assets):
    """Tests the method ``add_asset`` of the class ``InventoryClient``."""
    asset_id = AssetID('type_created', 'identifier_created')
    asset = Asset(asset_id)

    timestamp = datetime.fromisoformat('2022-01-01T01:00:00+00:00')
    expiration = datetime.fromisoformat('2022-01-07T01:00:00+00:00')

    created_asset = cli.add_asset(asset, expiration, timestamp)

    assert created_asset.vid is not None
    assert created_asset.asset_id.type == asset.asset_id.type
    assert created_asset.asset_id.identifier == asset.asset_id.identifier
    assert created_asset.time_attr.first_seen == timestamp
    assert created_asset.time_attr.last_seen == timestamp
    assert created_asset.time_attr.expiration == expiration

    final_assets = init_assets + [created_asset]
    assert compare_unsorted_list(cli.assets(), final_assets, lambda x: x.vid)


def test_add_asset_empty_type_identifier(cli, init_assets):
    """Tests the method ``add_asset`` of the class ``InventoryClient`` with an
    empty type or identifier string."""
    timestamp = datetime.fromisoformat('2022-01-01T01:00:00+00:00')
    expiration = datetime.fromisoformat('2022-01-07T01:00:00+00:00')

    with pytest.raises(ValueError, match='invalid asset_id'):
        cli.add_asset(
            Asset(AssetID('', 'identifier_created')), expiration, timestamp)
    assert compare_unsorted_list(cli.assets(), init_assets, lambda x: x.vid)

    with pytest.raises(ValueError, match='invalid asset_id'):
        cli.add_asset(
            Asset(AssetID('type_created', '')), expiration, timestamp)
    assert compare_unsorted_list(cli.assets(), init_assets, lambda x: x.vid)


def test_add_asset_conflict_error(cli, init_assets):
    """Tests the method ``add_asset`` of the class ``InventoryClient`` with an
    already existing asset."""
    asset_id = init_assets[2].asset_id
    asset = Asset(asset_id)

    timestamp = datetime.fromisoformat('2022-01-01T01:00:00+00:00')
    expiration = datetime.fromisoformat('2022-01-07T01:00:00+00:00')

    with pytest.raises(ConflictError, match=f'.*{asset_id}.*') as exc_info:
        cli.add_asset(asset, expiration, timestamp)

    assert exc_info.value.name == asset_id

    assert compare_unsorted_list(cli.assets(), init_assets, lambda x: x.vid)


def test_update_asset_future_timestamp(cli, init_assets):
    """Tests the method ``update_asset`` of the class ``InventoryClient``."""
    timestamp = datetime.fromisoformat('2024-01-01T01:00:00+00:00')
    expiration = datetime.fromisoformat('2024-01-07T01:00:00+00:00')

    updated_asset = cli.update_asset(
        init_assets[2].vid, init_assets[2], expiration, timestamp)

    assert updated_asset.vid == init_assets[2].vid
    assert updated_asset.asset_id == init_assets[2].asset_id
    assert updated_asset.time_attr.first_seen == \
        init_assets[2].time_attr.first_seen
    assert updated_asset.time_attr.last_seen == timestamp
    assert updated_asset.time_attr.expiration == expiration

    final_assets = init_assets[:2] + init_assets[3:] + [updated_asset]
    assert compare_unsorted_list(cli.assets(), final_assets, lambda x: x.vid)


def test_update_asset_past_timestamp(cli, init_assets):
    """Tests the method ``update_asset`` of the class ``InventoryClient``."""
    timestamp = datetime.fromisoformat('2000-01-01T01:00:00+00:00')
    expiration = datetime.fromisoformat('2022-01-07T01:00:00+00:00')

    updated_asset = cli.update_asset(
        init_assets[2].vid, init_assets[2], expiration, timestamp)

    assert updated_asset.vid == init_assets[2].vid
    assert updated_asset.asset_id == init_assets[2].asset_id
    assert updated_asset.time_attr.first_seen == timestamp
    assert updated_asset.time_attr.last_seen == \
        init_assets[2].time_attr.last_seen
    assert updated_asset.time_attr.expiration == \
        init_assets[2].time_attr.expiration

    final_assets = init_assets[:2] + init_assets[3:] + [updated_asset]
    assert compare_unsorted_list(cli.assets(), final_assets, lambda x: x.vid)


def test_update_asset_in_between_timestamp(cli, init_assets):
    """Tests the method ``update_asset`` of the class ``InventoryClient``."""
    timestamp = datetime.fromisoformat('2021-07-04T01:00:00+00:00')
    expiration = datetime.fromisoformat('2024-01-07T01:00:00+00:00')

    updated_asset = cli.update_asset(
        init_assets[2].vid, init_assets[2], expiration, timestamp)

    assert updated_asset.vid == init_assets[2].vid
    assert updated_asset.asset_id == init_assets[2].asset_id
    assert updated_asset.time_attr == init_assets[2].time_attr

    assert compare_unsorted_list(cli.assets(), init_assets, lambda x: x.vid)


def test_update_asset_vid_not_found_error(cli, init_assets):
    """Tests the method ``update_asset`` of the class ``InventoryClient`` with
    an unknown ``vid``."""
    timestamp = datetime.fromisoformat('2024-01-01T01:00:00+00:00')
    expiration = datetime.fromisoformat('2024-01-07T01:00:00+00:00')

    with pytest.raises(NotFoundError, match='.*13371337.*') as exc_info:
        cli.update_asset(13371337, init_assets[2], expiration, timestamp)

    assert exc_info.value.name == 13371337

    assert compare_unsorted_list(cli.assets(), init_assets, lambda x: x.vid)


def test_update_asset_asset_id_not_found_error(cli, init_assets):
    """Tests the method ``update_asset`` of the class ``InventoryClient`` with
    an unknown ``asset_id``."""
    timestamp = datetime.fromisoformat('2024-01-01T01:00:00+00:00')
    expiration = datetime.fromisoformat('2024-01-07T01:00:00+00:00')

    asset_id = AssetID(init_assets[2].asset_id.type, 'identifier1337')
    asset = Asset(asset_id)

    with pytest.raises(
        NotFoundError,
        match=f'.*{init_assets[2].vid}.*',
    ) as exc_info:
        cli.update_asset(init_assets[2].vid, asset, expiration, timestamp)

    assert exc_info.value.name == init_assets[2].vid

    assert compare_unsorted_list(cli.assets(), init_assets, lambda x: x.vid)


def test_set_asset(cli, init_assets):
    """Tests the method ``set_asset`` of the class ``InventoryClient``."""
    asset_id = AssetID('type_created', 'identifier_created')
    asset = Asset(asset_id)

    timestamp = datetime.fromisoformat('2022-01-01T01:00:00+00:00')
    expiration = datetime.fromisoformat('2022-01-07T01:00:00+00:00')

    (updated_asset, exists) = cli.set_asset(asset, expiration, timestamp)

    assert not exists
    assert updated_asset.vid is not None
    assert updated_asset.asset_id.type == asset.asset_id.type
    assert updated_asset.asset_id.identifier == asset.asset_id.identifier
    assert updated_asset.time_attr.first_seen == timestamp
    assert updated_asset.time_attr.last_seen == timestamp
    assert updated_asset.time_attr.expiration == expiration

    final_assets = init_assets + [updated_asset]
    assert compare_unsorted_list(cli.assets(), final_assets, lambda x: x.vid)


def test_set_asset_empty_type_identifier(cli, init_assets):
    """Tests the method ``set_asset`` of the class ``InventoryClient`` with an
    empty type or identifier string."""
    timestamp = datetime.fromisoformat('2022-01-01T01:00:00+00:00')
    expiration = datetime.fromisoformat('2022-01-07T01:00:00+00:00')

    with pytest.raises(ValueError, match='invalid asset_id'):
        cli.set_asset(
            Asset(AssetID('', 'identifier_created')), expiration, timestamp)
    assert compare_unsorted_list(cli.assets(), init_assets, lambda x: x.vid)

    with pytest.raises(ValueError, match='invalid asset_id'):
        cli.set_asset(
            Asset(AssetID('type_created', '')), expiration, timestamp)
    assert compare_unsorted_list(cli.assets(), init_assets, lambda x: x.vid)


def test_set_asset_update_past_timestamp(cli, init_assets):
    """Tests the method ``set_asset`` of the class ``InventoryClient`` with
    an existing asset and ``timestamp < first_seen``."""
    asset_id = init_assets[2].asset_id
    asset = Asset(asset_id)

    timestamp = datetime.fromisoformat('2000-01-01T01:00:00+00:00')
    expiration = datetime.fromisoformat('2022-01-07T01:00:00+00:00')

    (updated_asset, exists) = cli.set_asset(asset, expiration, timestamp)

    assert exists
    assert updated_asset.vid is not None
    assert updated_asset.asset_id.type == asset.asset_id.type
    assert updated_asset.asset_id.identifier == asset.asset_id.identifier
    assert updated_asset.time_attr.first_seen == timestamp
    assert updated_asset.time_attr.last_seen == \
        init_assets[2].time_attr.last_seen
    assert updated_asset.time_attr.expiration == \
        init_assets[2].time_attr.expiration

    final_assets = init_assets[:2] + init_assets[3:] + [updated_asset]
    assert compare_unsorted_list(cli.assets(), final_assets, lambda x: x.vid)


def test_set_asset_update_future_timestamp(cli, init_assets):
    """Tests the method ``set_asset`` of the class ``InventoryClient`` with
    an existing asset and ``timestamp > last_seen``."""
    asset_id = init_assets[2].asset_id
    asset = Asset(asset_id)

    timestamp = datetime.fromisoformat('2024-01-01T01:00:00+00:00')
    expiration = datetime.fromisoformat('2024-01-07T01:00:00+00:00')

    (updated_asset, exists) = cli.set_asset(asset, expiration, timestamp)

    assert exists
    assert updated_asset.vid is not None
    assert updated_asset.asset_id.type == asset.asset_id.type
    assert updated_asset.asset_id.identifier == asset.asset_id.identifier
    assert updated_asset.time_attr.first_seen == \
        init_assets[2].time_attr.first_seen
    assert updated_asset.time_attr.last_seen == timestamp
    assert updated_asset.time_attr.expiration == expiration

    final_assets = init_assets[:2] + init_assets[3:] + [updated_asset]
    assert compare_unsorted_list(cli.assets(), final_assets, lambda x: x.vid)


def test_set_asset_update_in_between_timestamp(cli, init_assets):
    """Tests the method ``set_asset`` of the class ``InventoryClient`` with
    an existing asset and ``first_seen < timestamp < last_seen."""
    asset_id = init_assets[2].asset_id
    asset = Asset(asset_id)

    timestamp = datetime.fromisoformat('2021-07-04T01:00:00+00:00')
    expiration = datetime.fromisoformat('2024-01-07T01:00:00+00:00')

    (updated_asset, exists) = cli.set_asset(asset, expiration, timestamp)

    assert exists
    assert updated_asset.vid is not None
    assert updated_asset.asset_id.type == asset.asset_id.type
    assert updated_asset.asset_id.identifier == asset.asset_id.identifier
    assert updated_asset.time_attr == init_assets[2].time_attr

    assert compare_unsorted_list(cli.assets(), init_assets, lambda x: x.vid)


# Parents.


def test_parents(cli, init_parents):
    """Tests the method ``parents`` of the class ``InventoryClient`."""
    for vid, parents in init_parents.items():
        assert compare_unsorted_list(
            cli.parents(vid), parents, lambda x: x.eid)


def test_parents_pagination(cli, init_parents):
    """Tests the pagination mode of the method ``parents`` of the class
    ``InventoryClient``."""
    vid = list(init_parents)[0]
    parents = init_parents[vid]

    assert compare_unsorted_list(
        cli.parents(vid, 1, 2), parents[2:4], lambda x: x.eid)
    assert compare_unsorted_list(
        cli.parents(vid, 0, 2), parents[0:2], lambda x: x.eid)
    assert compare_unsorted_list(
        cli.parents(vid, 1, 3), parents[3:4], lambda x: x.eid)
    assert compare_unsorted_list(
        cli.parents(vid, 1, 1), parents[1:2], lambda x: x.eid)
    assert compare_unsorted_list(
        cli.parents(vid, 0, 1000), parents, lambda x: x.eid)


def test_parents_not_found_error(cli):
    """Tests the method ``parents`` of the class ``InventoryClient`` with an
    unknown ``vid``."""
    with pytest.raises(NotFoundError, match=r'.*13371337.*') as exc_info:
        cli.parents(13371337)

    assert exc_info.value.name == 13371337


def test_set_parent_of(cli, init_parents, init_assets):
    """Tests the method ``set_parent_of`` of the class ``InventoryClient``."""
    vid = list(init_parents)[0]
    parents = init_parents[vid]

    parent_vid = init_assets[8].vid

    parentof = ParentOf(parent_vid, vid)

    timestamp = datetime.fromisoformat('2022-01-01T01:00:00+00:00')
    expiration = datetime.fromisoformat('2022-01-07T01:00:00+00:00')

    (updated_parentof, exists) = cli.set_parent_of(
        parentof, expiration, timestamp)

    assert not exists
    assert updated_parentof.eid is not None
    assert updated_parentof.child_vid == vid
    assert updated_parentof.parent_vid == parent_vid
    assert updated_parentof.time_attr.first_seen == timestamp
    assert updated_parentof.time_attr.last_seen == timestamp
    assert updated_parentof.time_attr.expiration == expiration

    final_parents = parents + [updated_parentof]
    assert compare_unsorted_list(
        cli.parents(vid), final_parents, lambda x: x.eid)


def test_set_parent_of_past_timestamp(cli, init_parents):
    """Tests the method ``set_parent_of`` of the class ``InventoryClient`` with
    an exissting edge and ``timestamp < first_seen``."""
    vid = list(init_parents)[0]
    parents = init_parents[vid]

    timestamp = datetime.fromisoformat('2000-01-01T01:00:00+00:00')
    expiration = datetime.fromisoformat('2022-01-07T01:00:00+00:00')

    (updated_parentof, exists) = cli.set_parent_of(
        parents[2], expiration, timestamp)

    assert exists
    assert updated_parentof.eid is not None
    assert updated_parentof.child_vid == parents[2].child_vid
    assert updated_parentof.parent_vid == parents[2].parent_vid
    assert updated_parentof.time_attr.first_seen == timestamp
    assert updated_parentof.time_attr.last_seen == \
        parents[2].time_attr.last_seen
    assert updated_parentof.time_attr.expiration == \
        parents[2].time_attr.expiration

    final_parents = parents[:2] + parents[3:] + [updated_parentof]
    assert compare_unsorted_list(
        cli.parents(vid), final_parents, lambda x: x.eid)


def test_set_parent_of_future_timestamp(cli, init_parents):
    """Tests the method ``set_parent_of`` of the class ``InventoryClient`` with
    an exissting edge and ``timestamp > last_seen``."""
    vid = list(init_parents)[0]
    parents = init_parents[vid]

    timestamp = datetime.fromisoformat('2024-01-01T01:00:00+00:00')
    expiration = datetime.fromisoformat('2024-01-07T01:00:00+00:00')

    (updated_parentof, exists) = cli.set_parent_of(
        parents[2], expiration, timestamp)

    assert exists
    assert updated_parentof.eid is not None
    assert updated_parentof.child_vid == parents[2].child_vid
    assert updated_parentof.parent_vid == parents[2].parent_vid
    assert updated_parentof.time_attr.first_seen == \
        parents[2].time_attr.first_seen
    assert updated_parentof.time_attr.last_seen == timestamp
    assert updated_parentof.time_attr.expiration == expiration

    final_parents = parents[:2] + parents[3:] + [updated_parentof]
    assert compare_unsorted_list(
        cli.parents(vid), final_parents, lambda x: x.eid)


def test_set_parent_of_in_between_timestamp(cli, init_parents):
    """Tests the method ``set_parent_of`` of the class ``InventoryClient`` with
    an exissting edge and ``first_seen < timestamp < last_seen``."""
    vid = list(init_parents)[0]
    parents = init_parents[vid]

    timestamp = datetime.fromisoformat('2021-07-04T01:00:00+00:00')
    expiration = datetime.fromisoformat('2024-01-07T01:00:00+00:00')

    (updated_parentof, exists) = cli.set_parent_of(
        parents[2], expiration, timestamp)

    assert exists
    assert updated_parentof.eid is not None
    assert updated_parentof.child_vid == parents[2].child_vid
    assert updated_parentof.parent_vid == parents[2].parent_vid
    assert updated_parentof.time_attr == parents[2].time_attr

    assert compare_unsorted_list(
        cli.parents(vid), parents, lambda x: x.eid)


def test_set_parent_of_same_child_parent(cli, init_assets):
    """Tests the method ``set_parent_of`` of the class ``InventoryClient``
    using the same vertex ID for both the parent asset and the child asset."""
    vid = init_assets[0].vid
    parentof = ParentOf(vid, vid)

    timestamp = datetime.fromisoformat('2022-01-01T01:00:00+00:00')
    expiration = datetime.fromisoformat('2022-01-07T01:00:00+00:00')

    with pytest.raises(ValueError, match=r'.*same.*'):
        cli.set_parent_of(parentof, expiration, timestamp)


def test_set_parent_of_not_found_error(cli, init_assets):
    """Tests the method ``set_parent_of`` of the class ``InventoryClient`` with
    unknown vertices."""
    vid = init_assets[0].vid

    timestamp = datetime.fromisoformat('2022-01-01T01:00:00+00:00')
    expiration = datetime.fromisoformat('2022-01-07T01:00:00+00:00')

    # Unknown parent_vid.
    with pytest.raises(NotFoundError, match=r'.*13371337.*') as exc_info:
        cli.set_parent_of(ParentOf(13371337, vid), expiration, timestamp)

    assert exc_info.value.name == 13371337

    # Unknown child_vid.
    with pytest.raises(NotFoundError, match=r'.*13381338.*') as exc_info:
        cli.set_parent_of(ParentOf(vid, 13381338), expiration, timestamp)

    assert exc_info.value.name == 13381338


def test_drop_parent_of(cli, init_parents):
    """Tests the method ``drop_parent_of`` of the class ``InventoryClient``."""
    vid = list(init_parents)[0]
    parents = init_parents[vid]

    cli.drop_parent_of(parents[2].eid)

    final_parents = parents[:2] + parents[3:]
    assert compare_unsorted_list(
        cli.parents(vid), final_parents, lambda x: x.eid)


def test_drop_parent_of_not_found_error(cli):
    """Tests the method ``drop_parent_of`` of the class ``InventoryClient``
    with an unknown ``eid``."""
    with pytest.raises(NotFoundError, match='.*13371337.*') as exc_info:
        cli.drop_parent_of(13371337)

    assert exc_info.value.name == 13371337


# Owners.


def test_owners(cli, init_owners):
    """Tests the method ``owners`` of the class ``InventoryClient`."""
    for asset_vid, owners in init_owners.items():
        assert compare_unsorted_list(
            cli.owners(asset_vid), owners, lambda x: x.eid)


def test_owners_pagination(cli, init_owners):
    """Tests the pagination mode of the method ``owners`` of the class
    ``InventoryClient``."""
    vid = list(init_owners)[0]
    owners = init_owners[vid]

    assert compare_unsorted_list(
        cli.owners(vid, 0, 2), owners[0:2], lambda x: x.eid)
    assert compare_unsorted_list(
        cli.owners(vid, 1, 2), owners[2:3], lambda x: x.eid)
    assert compare_unsorted_list(
        cli.owners(vid, 1, 1), owners[1:2], lambda x: x.eid)
    assert compare_unsorted_list(
        cli.owners(vid, 0, 1000), owners, lambda x: x.eid)


def test_owners_not_found_error(cli):
    """Tests the method ``owners`` of the class ``InventoryClient`` with an
    unknown ``vid``."""
    with pytest.raises(NotFoundError, match=r'.*13371337.*') as exc_info:
        cli.owners(13371337)

    assert exc_info.value.name == 13371337


def test_set_owns(cli, init_owners):
    """Tests the method ``set_owns`` of the class ``InventoryClient``."""
    asset_vid = list(init_owners)[0]
    owners = init_owners[asset_vid]

    team_vid = owners[1].team_vid

    owns = Owns(team_vid, asset_vid)

    start_time = datetime.fromisoformat('2022-01-01T01:00:00+00:00')
    end_time = datetime.fromisoformat('2022-01-07T01:00:00+00:00')

    (updated_owns, exists) = cli.set_owns(owns, start_time, end_time)

    assert exists
    assert updated_owns.eid is not None
    assert updated_owns.team_vid == team_vid
    assert updated_owns.asset_vid == asset_vid
    assert updated_owns.time_attr.start_time == start_time
    assert updated_owns.time_attr.end_time == end_time

    final_owners = owners[:1] + owners[2:] + [updated_owns]
    assert compare_unsorted_list(
        cli.owners(asset_vid), final_owners, lambda x: x.eid)


def test_set_owns_new(cli, init_owners, init_teams):
    """Tests the method ``set_owns`` of the class ``InventoryClient`` with a
    new relationship."""
    asset_vid = list(init_owners)[0]
    owners = init_owners[asset_vid]

    team_vid = init_teams[4].vid

    owns = Owns(team_vid, asset_vid)

    start_time = datetime.fromisoformat('2022-01-01T01:00:00+00:00')
    end_time = datetime.fromisoformat('2022-01-07T01:00:00+00:00')

    (updated_owns, exists) = cli.set_owns(owns, start_time, end_time)

    assert not exists
    assert updated_owns.eid is not None
    assert updated_owns.team_vid == team_vid
    assert updated_owns.asset_vid == asset_vid
    assert updated_owns.time_attr.start_time == start_time
    assert updated_owns.time_attr.end_time == end_time

    final_owners = owners + [updated_owns]
    assert compare_unsorted_list(
        cli.owners(asset_vid), final_owners, lambda x: x.eid)


def test_set_owns_not_found_error(cli, init_teams, init_assets):
    """Tests the method ``set_owns`` of the class ``InventoryClient`` with
    unknown vertices."""
    team_vid = init_teams[0].vid
    asset_vid = init_assets[0].vid

    start_time = datetime.fromisoformat('2022-01-01T01:00:00+00:00')
    end_time = datetime.fromisoformat('2022-01-07T01:00:00+00:00')

    # Unknown parent_vid.
    with pytest.raises(NotFoundError, match=r'.*13371337.*') as exc_info:
        cli.set_owns(Owns(13371337, asset_vid), start_time, end_time)

    assert exc_info.value.name == 13371337

    # Unknown child_vid.
    with pytest.raises(NotFoundError, match=r'.*13381338.*') as exc_info:
        cli.set_owns(Owns(team_vid, 13381338), start_time, end_time)

    assert exc_info.value.name == 13381338


def test_drop_owns(cli, init_owners):
    """Tests the method ``drop_owns`` of the class ``InventoryClient``."""
    vid = list(init_owners)[0]
    owners = init_owners[vid]

    cli.drop_owns(owners[1].eid)

    final_owners = owners[:1] + owners[2:]
    assert compare_unsorted_list(
        cli.owners(vid), final_owners, lambda x: x.eid)


def test_drop_owns_not_found_error(cli):
    """Tests the method ``drop_owns`` of the class ``InventoryClient`` with an
    unknown ``eid``."""
    with pytest.raises(NotFoundError, match='.*13371337.*') as exc_info:
        cli.drop_owns(13371337)

    assert exc_info.value.name == 13371337


# Misc.


def test_injection(cli):
    """Tests the method ``team_identifier`` of the class ``InventoryClient``
    with potentially dangerous characters."""
    with pytest.raises(NotFoundError) as exc_info:
        cli.team_identifier('identifier1337"\'}{)(][.,;\r\n')

    assert exc_info.value.name == 'identifier1337"\'}{)(][.,;\r\n'
