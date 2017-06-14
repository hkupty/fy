# encoding: utf-8
""" Type wrappers. """
import os
import codecs
from glob import glob
from functools import partial
from fy.tp.core import Functional


def change_extension(new_ext, fpath):
    fpath, fl = os.path.split(fpath)
    fname = fl.split(os.path.extsep)[0]
    return os.path.join(fpath, os.path.extsep.join([fname, new_ext]))


class Hierarchical(Functional):

    def child(self, *child):
        return self.map(lambda k: os.path.join(k, *child))

    def parent(self, child):
        return self.map(lambda k: os.path.split(k)[0])


class Lazy(Functional):

    def map(self, fn):
        return self.__class__(lambda *args: self._data(fn(*args)))

    def tee(self, fn):
        def t(*args):
            fn(*args)
            return self

        return self.__class__(t)

    def unwrap(self, *args):
        try:
            return self._data(*args) or True
        except Exception as e:
            print(e)
            return False

    def flatten(self):
        def l():
            k = self._data()
            if type(k) == self.__class__:
                return k.unwrap()
            return k
        return Lazy(l)


class Writer(Lazy):

    def apply(self, data):
        return self.unwrap(data)


class Reader(Functional):
    pass



class Path(Hierarchical):

    def coerce(self):
        if self.exists():
            if os.path.isdir(self._data):
                return Folder.bind(self._data)
        return File.bind(self._data)

    def __repr__(self):
        return "<Path={}>".format(self._data)

    def glob(self):
        return list(map(self.__class__.bind, glob(self._data)))

    def exists(self):
        return os.path.exists(self._data)

    def touch(self):
        if not os.path.exists(self._data):
            h, _ = os.path.split(self._data)
            if not os.path.exists(h):
                Folder(h).touch()
            self.create()

    def updateIf(self, new_value):
        if new_value:
            return self.__class__.bind(new_value)

        return self


class Folder(Path):

    def create(self):
        return os.mkdir(self._data)

    def __repr__(self):
        return "<Folder={}>".format(self._data)


class File(Path):

    def __repr__(self):
        return "<File={}>".format(self._data)

    def child(self, *child):
        return super().child(*child)

    def with_codec(self, write, read, extension):
        new_ext = partial(change_extension, extension)

        class CodecPath(self.__class__):

            @classmethod
            def bind(cls, data):
                return cls(new_ext(data))

            def __repr__(self):
                return "<{}File={}>".format(extension, self._data)

            def writer(self, mode='append'):
                return super().writer(mode=mode).map(write)

            def reader(self):
                return super().reader().map(read)

        return CodecPath.bind(self._data)

    def create(self):
        open(self._data, 'w').close()

    def writer(self, mode='append'):
        if mode in {'unique', }:
            def inc_suffix(fname):
                fname, *ext = fname.split('.')
                if '-' in fname:
                    p = fname.split('-')
                    p[-1] = str(int(p[-1]) + 1)
                    fname = '-'.join(p)
                else:
                    fname = '-'.join([fname, '1'])
                return '.'.join([fname, *ext])

            while self.exists():
                self = self.map(inc_suffix)

        if mode in {'unique', 'truncate'}:
            fmode = 'w'
        else:
            fmode = 'a'

        self.touch()

        def inner(content):
            with open(self._data, fmode) as b:
                b.write(content)

        return Writer(inner)

    def atomic_write(self, data, mode='append'):
        return self.writer(mode=mode).apply(data)

    def reader(self):
        with open(self._data, 'r') as b:
            return Reader.bind("\n".join(b.readlines()))

    def atomic_read(self):
        return self.reader().unwrap()


class CodecFile(File):

    def reader(self):
        return Reader.bind(codecs.open(self._data, 'r'))
