import operator
import os
from functools import reduce
from pathlib import Path

import requests
from constance import config
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from datamaker.utils.string import remove_query_string


def download_file(url, path_download, name=None, coerce=None):
    url_parsed = Path(remove_query_string(url))
    if name:
        name += url_parsed.suffix
    else:
        name = url_parsed.name

    media_url = os.path.join(config.BACKEND_HOST, 'media/')

    if config.MEDIA_ROOT and url.startswith(media_url):
        path = Path(config.MEDIA_ROOT) / url.replace(media_url, '')
    else:
        path = path_download / name
        if not path.is_file():
            r = requests.get(url, allow_redirects=True)
            open(str(path), 'wb').write(r.content)
    if coerce:
        path = coerce(path)
    return path


def files_url_to_path(files, coerce=None):
    path_download = Path(config.TEMP_ROOT) / 'media'
    path_download.mkdir(parents=True, exist_ok=True)
    for file_name in files:
        if isinstance(files[file_name], str):
            files[file_name] = download_file(
                files[file_name], path_download, coerce=coerce
            )
        else:
            files[file_name]['path'] = download_file(
                files[file_name].pop('url'), path_download, coerce=coerce
            )


def files_url_to_path_from_objs(objs, files_fields, coerce=None, is_list=False):
    if not is_list:
        objs = [objs]

    for obj in objs:
        for files_field in files_fields:
            try:
                files = reduce(operator.getitem, files_field.split('.'), obj)
                files_url_to_path(files, coerce=coerce)
            except KeyError:
                pass


def get_file_from_url(url):
    r = requests.get(url, allow_redirects=True)
    file = NamedTemporaryFile(delete=True)
    file.write(r.content)
    file.flush()
    return File(file, name=Path(remove_query_string(url)).name)


def json_default(value):
    if isinstance(value, Path):
        return str(value)
    raise TypeError
