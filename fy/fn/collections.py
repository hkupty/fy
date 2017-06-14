# encoding: utf-8
""" Helper functions and stuff. """


def identity(item):
    return item


def select_keys(dct, keys):
    if type(dct) != dict:
        dct = dct.__dict__
    return {k: v for k, v in dct.items() if k in keys}


def splitAtHead(lst):
    head = lst[:1]

    if head:
        return head[0], lst[1:]

    return None, []

def _update_with(base, key, fn):
    new = base.copy()
    new.update(fn(base.get(key)))
    return new


def update_with(base, key, fn):
    return _update_with(base, key, lambda val: {key: fn(val)})


def update(base, **kwargs):
    return _update_with(base, None, lambda _: kwargs)


def _update_in(base, path, update_fn, **kwargs):
    item, path = splitAtHead(path)

    if not item:
        return update_fn(base, **kwargs)
    else:
        return update_with(
            base, item,
            lambda _: _update_in(base[item], path, update_fn, **kwargs)
        )


def update_in(base, path, **kwargs):
    return _update_in(base, path, update, **kwargs)


def update_in_with(base, path, fn):
    return _update_in(base, path, fn)


def values(data):
    return list(data.values())


def keys(data):
    return list(data.keys())


def clean(lst):
    return list(filter(None, lst))
