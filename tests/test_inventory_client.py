import pytest

from helpers import compare_unsorted_list

from graph_asset_inventory_api.inventory.types import (
    Team,
    NotFoundException,
)


def test_teams(cli, init_teams):
    teams = cli.teams()
    assert compare_unsorted_list(teams, init_teams, lambda x: x.identifier)


def test_teams_page(cli, init_teams):
    assert compare_unsorted_list(
        cli.teams_page(1, 2), init_teams[2:4], lambda x: x.identifier)
    assert compare_unsorted_list(
        cli.teams_page(0, 2), init_teams[0:2], lambda x: x.identifier)
    assert compare_unsorted_list(
        cli.teams_page(2, 2), init_teams[4:5], lambda x: x.identifier)
    assert compare_unsorted_list(
        cli.teams_page(1, 1), init_teams[1:2], lambda x: x.identifier)
    assert compare_unsorted_list(
        cli.teams_page(0, 1000), init_teams, lambda x: x.identifier)


def test_team(cli, init_teams):
    team = cli.team(init_teams[2].vid)
    assert team == init_teams[2]


def test_team_not_found(cli):
    with pytest.raises(NotFoundException):
        cli.team(13371337)


def test_team_identifier(cli, init_teams):
    team = cli.team_identifier(init_teams[2].identifier)
    assert team == init_teams[2]


def test_team_identifier_not_found(cli):
    with pytest.raises(NotFoundException):
        cli.team_identifier('identifier1337')


def test_drop_team(cli, init_teams):
    cli.drop_team(init_teams[2].vid)

    filter_teams = init_teams[:2] + init_teams[3:]
    assert compare_unsorted_list(
        cli.teams(), filter_teams, lambda x: x.identifier)


def test_drop_team_non_existent(cli, init_teams):
    cli.drop_team(13371337)

    assert compare_unsorted_list(
        cli.teams(), init_teams, lambda x: x.identifier)


def test_add_team(cli, init_teams):
    team = Team('identifier_created', 'name_created')
    created_team = cli.add_team(team)

    assert created_team.vid is not None
    assert created_team.identifier == team.identifier
    assert created_team.name == team.name

    final_teams = init_teams + [created_team]
    assert compare_unsorted_list(
        cli.teams(), final_teams, lambda x: x.identifier)


def test_add_team_existent(cli, init_teams):
    team = Team(init_teams[2].identifier, 'name_modified')
    created_team = cli.add_team(team)

    assert created_team.vid == init_teams[2].vid
    assert created_team.identifier == init_teams[2].identifier
    assert created_team.name == team.name

    final_teams = init_teams[:2] + init_teams[3:] + [created_team]
    assert compare_unsorted_list(
        cli.teams(), final_teams, lambda x: x.identifier)
