from urllib.parse import urlparse, urlunparse


def remove_query_string(url):
    parsed = urlparse(url)
    cleaned_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))
    return cleaned_url
