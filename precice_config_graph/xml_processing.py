# Use lxml instead of built-in, since it allows ignoring undefined namespaces.
# preCICE configs use tag names like `data:scalar`, which are like namespaces.
from lxml import etree


def parse_file(path: str) -> etree._Element:
    parser = etree.XMLParser(recover=True, remove_comments=True)
    tree = etree.fromstring(open(path, "rb").read(), parser)
    return tree


# Function to get a boolean value from a string
# Implemented according to how preCICE itself implements this method:
# https://github.com/precice/precice/blob/2819cd61b747c35ae5c8ddd78866e913144c6ca4/src/utils/String.cpp#L56-L64
def convert_string_to_bool(string: str) -> bool:
    string = string.lower()
    if string == "1" or string == "yes" or string == "true" or string == "on":
        return True

    return False
