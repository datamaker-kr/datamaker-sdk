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


def dataset_batch(dataset, batch_size):
    return [dataset[data:data + batch_size] for data in range(0, len(dataset), batch_size)]
