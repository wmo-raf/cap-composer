from collections import OrderedDict
from io import BytesIO
from xml.dom import minidom

from cairosvg import svg2png
from django.utils.safestring import mark_safe
from magic import from_file
from wagtailiconchooser.utils import get_svg_icons


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


def rasterize_svg_to_png(icon_name, fill_color=None):
    svg_icons = get_svg_icons()

    svg_str = svg_icons.get(icon_name)

    if not svg_str:
        return None

    doc = minidom.parseString(svg_str)
    svg = doc.getElementsByTagName("svg")
    if svg:
        svg = svg[0]

        svg.setAttribute("height", "26")
        svg.setAttribute("width", "26")

        if fill_color:
            svg.setAttribute("fill", fill_color)
            svg_str = mark_safe(svg.toxml())

    svg_bytes = svg_str.encode('utf-8')

    in_buf = BytesIO(svg_bytes)

    # Prepare a buffer for output
    out_buf = BytesIO()

    # Rasterise the SVG to PNG
    svg2png(file_obj=in_buf, write_to=out_buf)
    out_buf.seek(0)

    # Return a Willow PNGImageFile
    return out_buf
