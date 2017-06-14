# encoding: utf-8
"""Abstract functional type.

This creates the foundation of other 'functional' types."""


class Functional(object):

    transform = identity

    def __init__(self, data):
        self._data = data

    @classmethod
    def bind(cls, data):
        return cls(data)

    @classmethod
    def bind_from_monad(cls, data):
        return cls.bind(cls.transform(data))

    def rebind(self, cls):
        return cls.bind_from_monad(self.unwrap())

    def unwrap(self):
        return self._data

    def map(self, fn):
        return self.__class__.bind(fn(self._data))

    def flatten(self):
        if type(self._data) == self.__class__:
            return self._data
        return self

    def flatMap(self, fn):
        return self.map(fn).flatten()
