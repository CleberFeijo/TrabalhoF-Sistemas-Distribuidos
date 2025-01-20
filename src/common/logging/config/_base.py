__all__ = '_BaseConfig',


class _BaseConfig(dict):
    def __init__(self, **kwargs):
        super().__init__()

        for key, value in kwargs.items():
            if value is None:
                continue
            self[key] = value
