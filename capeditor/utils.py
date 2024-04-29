from collections import OrderedDict

from magic import from_file


def file_path_mime(file_path):
    mimetype = from_file(file_path, mime=True)
    return mimetype


def order_dict_by_keys(input_dict, key_order):
    """
    Orders a dictionary based on a provided list of keys.

    Args:
    - input_dict: The dictionary to be ordered.
    - key_order: A list of keys specifying the desired order.

    Returns:
    - ordered_dict: The ordered dictionary.
    """
    ordered_dict = OrderedDict()
    for key in key_order:
        if key in input_dict:
            ordered_dict[key] = input_dict[key]
    return ordered_dict


def dict_add_after_key(original_dict, key_to_insert_after, new_key, new_value):
    """
    Insert a new key-value pair after the specified key in the dictionary.

    Parameters:
    - original_dict: The original dictionary.
    - key_to_insert_after: The key after which the new key-value pair should be inserted.
    - new_key: The key to be inserted after 'key_to_insert_after'.
    - new_value: The value corresponding to the new_key.

    Returns:
    - The modified dictionary.
    """

    if key_to_insert_after not in original_dict:
        return original_dict

    new_dict = OrderedDict()
    for key, value in original_dict.items():
        new_dict[key] = value
        if key == key_to_insert_after:
            new_dict[new_key] = new_value
    return new_dict
