import os
from pathlib import Path

import requests
from django.conf import settings
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile


def download_file(url, path_download, name=None):
    if name:
        name += Path(url).suffix
    else:
        name = Path(url).name

    media_url = os.path.join(settings.DATAMAKER_HOST, 'media/')

    if url.startswith(media_url):
        path = Path(settings.DATAMAKER_MEDIA_ROOT) / url.replace(media_url, '')
    else:
        path = path_download / name
        if not path.is_file():
            r = requests.get(url, allow_redirects=True)
            open(str(path), 'wb').write(r.content)
    return path


def files_url_to_path(files):
    path_download = Path('/tmp/agent/media')
    path_download.mkdir(parents=True, exist_ok=True)
    for file_name in files:
        url = files[file_name]
        files[file_name] = download_file(url, path_download)


def get_file_from_url(url):
    r = requests.get(url, allow_redirects=True)
    file = NamedTemporaryFile(delete=True)
    file.write(r.content)
    file.flush()
    return File(file, name=Path(url).name)
