import struct
from abc import ABC, abstractmethod
from .renderer import Renderer

import chardet
import charset_normalizer
import ctypes

class WireType:
    Varint       = 0
    Fixed64      = 1
    Struct       = 2
    Deprecated_3 = 3
    Deprecated_4 = 4
    Fixed32      = 5

def wire_type_str(t):
    if t == WireType.Varint:
        return 'varint'
    elif t == WireType.Fixed64:
        return 'fixed64/double'
    elif t == WireType.Struct:
        return 'string'
    elif t == WireType.Fixed32:
        return 'fixed32/float'
    else:
        return 'Unknown wire type'

class IdType:
    def __init__(self, id, wire_type, view):
        self.id = id
        self.wire_type = wire_type
        self.view = view

    # for the part:
    #     [42] 8 string: 
    def render(self, indent_level, r):
        r.add_indent(indent_level)
        r.add_normal('[')
        r.add_idtype(' '.join(format(x, '02x') for x in self.view))
        r.add_normal('] ')
        r.add_id(str(self.id) + ' ')
        r.add_type(wire_type_str(self.wire_type))
        r.add_normal(': ')

class Chunk(ABC):
    def __init__(self, idtype: IdType, view: memoryview):
        self.idtype = idtype
        self.view = view

    @abstractmethod
    def render(self, indent_level: int, r: Renderer):
        pass

class Varint(Chunk):
    def render(self, indent_level, r):
        self.idtype.render(indent_level, r)

        # convert u64 -> i64
        # i64 should be enough, no need for u64
        i64 = ctypes.c_int64(self.view).value
        r.add_num(str(i64))

        r.add_normal(' (')
        r.add_num(str(hex(self.view)))
        r.add_normal(')')

class FixedN(Chunk):
    # displayed as:
    #   unsigned (signed if negative) (hex) (float)
    def render(self, indent_level, r):
        u = struct.unpack(self.utag, self.view)[0] # unsigned
        i = struct.unpack(self.itag, self.view)[0] # signed
        f = struct.unpack(self.ftag, self.view)[0] # float

        self.idtype.render(indent_level, r)
        r.add_normal(str(u))
        if i < 0:
            r.add_normal(f" ({str(i)})")

        r.add_normal(f" ({hex(u)}) ({str(f)})")

class Fixed32(FixedN):
    def __init__(self, idtype: IdType, view: memoryview):
        super().__init__(idtype, view)
        self.utag = '<I'
        self.itag = '<i'
        self.ftag = '<f'

class Fixed64(FixedN):
    def __init__(self, idtype: IdType, view: memoryview):
        super().__init__(idtype, view)
        self.utag = '<q'
        self.itag = '<Q'
        self.ftag = '<d'

class Struct(Chunk):

    def __init__(self, idtype: IdType, view: memoryview):
        super().__init__(idtype, view)
        self.children = []

    # return (
    #   decoded bytes: bytes
    #   encoding name: str
    #   decode success: bool
    # )
    def decode_str(self) -> (bytes, str, bool):
        view_bytes = self.view.tobytes()
        try:
            # `chardet` is way more accurate, but very slow with large bytes(4 seconds on 50k bytes)
            # `charset_normalizer` shows wrong result with small bytes, but very performant with long bytes
            if len(view_bytes) <= 200:
                detected = chardet.detect(view_bytes)
            else:
                detected = charset_normalizer.detect(view_bytes)

            if detected['confidence'] < 0.9:
                raise Exception()

            encoding = detected['encoding']

            decoded = view_bytes.decode(encoding)
            
            return decoded, encoding, True
        except:
            pass

        return view_bytes, '', False

    def render_str(self, s:str, encoding:str, r:Renderer):
        if encoding not in ['ascii']:
            r.add_normal(f"[{encoding}] ")

        r.add_str(s)

    def render(self, indent_level, r):
        self.idtype.render(indent_level, r)
        r.add_normal(f"({str(len(self.view))}) ")

        decoded, encoding, is_str = self.decode_str()

        if is_str:
            if self.children:
                if decoded.isprintable():
                    self.render_str(decoded, encoding, r)
            else:
                self.render_str(decoded, encoding, r)

                # Also show hex if:
                # 1. it contains non-printable characters
                # 2. it is short, less than 8 bytes
                if not decoded.isprintable() or 0 < len(self.view) <= 8:
                    r.add_normal(' (')
                    r.add_bin(self.view)
                    r.add_normal(')')
        else:
            if not self.children:
                # show as binary
                r.add_bin(self.view)
                
        # 2. show as child struct
        if self.children:
            for ch in self.children:
                r.add_newline()
                ch.render(indent_level+1, r)
