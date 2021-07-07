"""Helper functions shared across tests."""


def compare_unsorted_list(list_a, list_b, sort_key):
    """Compares two unsorted lists."""
    return sorted(list_a, key=sort_key) == sorted(list_b, key=sort_key)
