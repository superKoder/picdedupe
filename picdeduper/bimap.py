
class BiMap(dict):
    """
    A dictionary where you can get the key by value and the value by key.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        mirror = dict()
        for key, value in self.items():
            mirror[value] = key
        self.update(mirror)

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        super().__setitem__(value, key)

    def __delitem__(self, key):
        value = super().__getitem__(key)
        super().__delitem__(key)
        super().__delitem__(value)