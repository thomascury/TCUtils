import os
import hashlib
import sys
from codecs import open


def check_md5sum(filepath, encoding=None):
    if encoding is None:
        encoding = sys.getfilesystemencoding()
    with open(filepath, 'rb', encoding=encoding) as f:
        content = f.read()
    hash_object = hashlib.md5()
    hash_object.update(content)
    return hash_object.hexdigest()


def copy(source, destination, override=False, source_encoding=None, destination_encoding=None):
    if not os.path.exists(source):
        raise OSError("Source file does not exist.")
    if not os.isdir(source):
        raise OSError("Source is not a file, thus it can't be copied.")
    if os.path.exists(destination):
        if not override:
            raise OSError("Destination file already exists.")
        elif os.isdir(destination):
            raise OSError("Can't override a folder with a file.")
    if source_encoding is None:
        source_encoding = sys.getfilesystemencoding()
    if destination_encoding is None:
        destination_encoding = sys.getfilesystemencoding()

    with open(source, 'rb', encoding=source_encoding) as src_f, \
            open(destination, 'wb', encoding=destination_encoding) as dst_f:
        dst_f.write(src_f.read())

    if check_md5sum(source) != check_md5sum(destination):
        raise OSError("Copy failed.")
