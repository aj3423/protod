import itertools
import struct
from typing import List

from google.protobuf.internal.decoder import _DecodeVarint

from .definition import WireType
from .field import Field, Fixed, IdType, RepeatedField, Struct, Varint
from .renderer import ConsoleRenderer
from .util import detect_multi_charset


# 0	Varint	int32, int64, uint32, uint64, sint32, sint64, bool, enum
# 1	64-bit	fixed64, sfixed64, double
# 2	Length-delimited	string, bytes, embedded messages, packed repeated fields
# 3	Start group	groups (deprecated)
# 4	End group	groups (deprecated)
# 5	32-bit	fixed32, sfixed32, float
def decode_1_field(str_decoder, parent: Field, view: memoryview) -> tuple[Field, int]:
    pos = 0

    id_type, pos = _DecodeVarint(view, 0)

    if pos >= len(view):
        raise Exception("not enough data for any further wire type")

    id = id_type >> 3

    if id > 536870911:  # max field: 2^29 - 1 == 536870911
        raise Exception("field number > max field value 2^29-1")

    wire_type = id_type & 7

    idtype_bytes = view[0:pos]

    ret = None

    if wire_type == WireType.Varint:  # 0
        if pos >= len(view):
            raise Exception("not enough data for wire type 0(varint)")

        u64, pos = _DecodeVarint(view, pos)

        ret = Varint(u64)

    elif wire_type == WireType.Fixed32:  # 5
        if pos + 4 > len(view):
            raise Exception("not enough data for wire type 5(fixed32)")

        _4bytes = view[pos : pos + 4]
        pos += 4

        u = struct.unpack("<I", _4bytes)[0]  # unsigned
        i = struct.unpack("<i", _4bytes)[0]  # signed
        f = struct.unpack("<f", _4bytes)[0]  # float
        ret = Fixed(u, i, f)

    elif wire_type == WireType.Fixed64:  # 1
        if pos + 8 > len(view):
            raise Exception("not enough data for wire type 1(fixed64)")

        _8bytes = view[pos : pos + 8]
        pos += 8

        u = struct.unpack("<q", _8bytes)[0]  # unsigned
        i = struct.unpack("<Q", _8bytes)[0]  # signed
        f = struct.unpack("<d", _8bytes)[0]  # float

        ret = Fixed(u, i, f)

    elif wire_type == WireType.Struct:  # 2
        s_len, pos = _DecodeVarint(view, pos)

        if pos + s_len > len(view):
            raise Exception("not enough data for wire type 2(string)")

        view_field = view[pos : pos + s_len]
        pos += s_len

        as_str, encoding, is_str = str_decoder(view_field)
        ret = Struct(view_field, as_str, encoding, is_str)

        try:
            # if decode successfully, it's child struct, not just binary bytes
            ret.as_fields = decode_all_fields(str_decoder, ret, view_field)
        except:
            pass

    elif wire_type == WireType.Deprecated_3:  # 3
        raise Exception("[proto 3] found, looks like invalid proto bytes")

    elif wire_type == WireType.Deprecated_4:  # 4
        raise Exception("[proto 4] found, looks like invalid proto bytes")
    else:
        raise Exception(f"Unknown wire type {wire_type} of id_type {id_type}")

    ret.idtype = IdType(id, wire_type, idtype_bytes)
    ret.parent = parent

    return ret, pos


def decode_all_fields(str_decoder, parent: Field, view: memoryview) -> List[Field]:
    pos = 0
    fields = []

    while pos < len(view):
        try:
            field, field_len = decode_1_field(str_decoder, parent, view[pos:])
        except:
            raise Exception(f"field: {view[pos:].tobytes()}")

        fields.append(field)
        pos += field_len

    # group fields with same id to a RepeatedField
    ret = []
    for _, group in itertools.groupby(fields, lambda f: f.idtype.id):

        items = list(group)

        if len(items) == 1:  # single field
            ret.append(items[0])
        else:  # repeated fields
            repeated = RepeatedField(items)
            repeated.idtype = items[0].idtype
            repeated.parent = items[0].parent
            ret.append(repeated)

    return ret


def dump(
    data: bytes,
    renderer=ConsoleRenderer(),
    str_decoder=detect_multi_charset,
):
    view = memoryview(data)

    fields = decode_all_fields(str_decoder=str_decoder, parent=None, view=view)

    for ch in fields:
        ch.render(renderer)

    return renderer.build_result()
