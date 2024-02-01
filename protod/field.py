import ctypes
from abc import ABC, abstractmethod

from .renderer import Renderer


class IdType:
    def __init__(self, id, wire_type, idtype_bytes):
        self.id = id
        self.wire_type = wire_type
        self.raw_bytes = idtype_bytes


class Field(ABC):
    def __init__(self):
        self.idtype = None
        self.parent = None

    def indent_level(self):
        lvl = 0
        p = self.parent
        while p is not None:
            lvl += 1
            p = p.parent

        return lvl

    @abstractmethod
    def render(self, r: Renderer):
        pass


class RepeatedField(Field):
    def __init__(self, items):
        self.items = items

    def render(self, r: Renderer):
        r.render_repeated_fields(self)


class Varint(Field):
    def __init__(self, u64):
        super().__init__()

        # convert u64 -> i64
        # i64 should be enough, no need for u64
        self.u64 = u64
        self.i64 = ctypes.c_int64(u64).value

    def render(self, r: Renderer):
        r.render_varint(self)


class Fixed(Field):
    def __init__(self, u, i, f):
        super().__init__()

        # u: unsigned form
        # i: signed form
        # f: float form
        self.u, self.i, self.f = u, i, f

    # displayed as:
    #   unsigned (signed if negative) (hex) (float)
    def render(self, r: Renderer):
        r.render_fixed(self)


class Struct(Field):

    def __init__(self, view: memoryview, as_str: bytes, encoding: str, is_str: bool):
        super().__init__()

        self.view = view  # raw memoryview
        self.as_fields = []  # this struc can be parsed to fields
        self.as_str, self.encoding, self.is_str = as_str, encoding, is_str

    def render(self, r: Renderer):
        r.render_struct(self)
