import urllib.parse
import uuid


def get_id():
    return int(str(int(uuid.uuid4()))[0:10])


def url_encode_tag(a_str):
    return urllib.parse.quote(a_str, safe='')


def url_decode_tag(a_str):
    return urllib.parse.unquote(a_str)


def make_decoded(a_str):
    if '%' in a_str:
        return url_decode_tag(a_str)
    else:
        return a_str


def make_encoded(a_str):
    """
    Check is a string needs encoding.

    If it does return it encoded.

    If not return it unencoded.
    """
    forbidden = [";", "/", "?", ":", "@", "=", "&", '"', "'", "<", ">",
                 "#", "{", "}", "|", "\\", "/", "^", "~", "[", "]", "`", " "]
    for char in a_str:
        if char in forbidden:
            print(a_str, ' needs encoding')
            return url_encode_tag(a_str)

    return a_str
