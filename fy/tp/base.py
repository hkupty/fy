# encoding: utf-8
"""Basic functional types.

This implements some base types, such as Option and Try."""
from fy.tp.core import Functional

class Option(Functional):

    @classmethod
    def bind(cls, data):
        if data is None:
            return Nil()
        return Some(data)


class Some(Option):

    def __repr__(self):
        return "<Some({})>".format(self._data)


class Nil(Option):

    def __repr__(self):
        return "<Nil>"

    def __init__(self):
        self._data = None

    def map(self, fn):
        return self


class Try(Functional):

    @classmethod
    def bind(cls, data):
        if isinstance(data, Exception):
            return Failure(data)
        return Success(data)
    
    def map(self, fn):
        try:
            return self.__class__.bind(fn(self._data))
        except Exception as e:
            return Failure(e)


class Success(Try):

    def __repr__(self):
        return "<Success({})>".format(self._data)


class Failure(Try):

    def __repr__(self):
        return "<Failure({})>".format(str(self._data))

    def map(self, fn):
        return self

    def recover(self, fn):
        return Try.bind(fn(self._data))

    def recoverWith(self, fn):
        return self.recover(fn).flatten()
