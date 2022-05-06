def get_default_url_conversion(url_conversion, **kwargs):
    defaults = {
        'files_fields': [],
        'coerce': None,
        'is_list': True
    }
    defaults.update(kwargs)
    if url_conversion:
        defaults.update(url_conversion)
    return defaults
