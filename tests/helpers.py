def compare_unsorted_list(list_a, list_b, sort_key):
    return sorted(list_a, key=sort_key) == sorted(list_b, key=sort_key)
