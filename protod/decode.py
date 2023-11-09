from typing import List

from google.protobuf.internal.decoder import _DecodeVarint

from .renderer import Renderer, ConsoleRenderer
from .chunk import Chunk, IdType, Fixed32, Fixed64, Varint, Struct, WireType

# 0	Varint	int32, int64, uint32, uint64, sint32, sint64, bool, enum
# 1	64-bit	fixed64, sfixed64, double
# 2	Length-delimited	string, bytes, embedded messages, packed repeated fields
# 3	Start group	groups (deprecated)
# 4	End group	groups (deprecated)
# 5	32-bit	fixed32, sfixed32, float
def decode_1_chunk(view: memoryview) -> (Chunk, int):
    pos = 0

    id_type, pos = _DecodeVarint(view, 0)

    if pos >= len(view):
        raise Exception("not enough data for any further wire type")

    id = id_type >> 3

    if id > 536870911: # max field: 2^29 - 1 == 536870911
        raise Exception("field number > max field value 2^29-1")

    wire_type = id_type & 7

    id_type_bytes = view[0:pos]

    if wire_type == WireType.Varint: # 0
        if pos >= len(view):
            raise Exception("not enough data for wire type 0(varint)")

        u64, pos = _DecodeVarint(view, pos)

        return Varint(IdType(id, wire_type, id_type_bytes), u64), pos

    elif wire_type == WireType.Fixed32: # 5
        if pos + 4 > len(view):
            raise Exception("not enough data for wire type 5(fixed32)")
        
        _4bytes = view[pos:pos+4]
        pos += 4

        return Fixed32(IdType(id, wire_type, id_type_bytes), _4bytes), pos
    elif wire_type == WireType.Fixed64: # 1
        if pos + 8 > len(view):
            raise Exception("not enough data for wire type 1(fixed64)")

        _8bytes = view[pos:pos+8]
        pos += 8

        return Fixed64(IdType(id, wire_type, id_type_bytes), _8bytes), pos

    elif wire_type == WireType.Struct: # 2
        s_len, pos = _DecodeVarint(view, pos)

        if pos + s_len > len(view):
            raise Exception("not enough data for wire type 2(string)")

        view_chunk = view[pos:pos+s_len]
        pos += s_len

        _struct = Struct(IdType(id, wire_type, id_type_bytes), view_chunk)

        try:
            chunks = decode_all_chunks(view_chunk)
            # if decode successfully, treat as struct
            _struct.children = chunks
        except:
            pass
        return _struct, pos

    elif wire_type == WireType.Deprecated_3: # 3
        raise Exception("[proto 3] found, looks like invalid proto bytes")

    elif wire_type == WireType.Deprecated_4: # 4
        raise Exception("[proto 4] found, looks like invalid proto bytes")

    else:
        raise Exception(f"Unknown wire type {wire_type} of id_type {id_type}")

def decode_all_chunks(view: memoryview) -> List[Chunk]:
    pos = 0
    ret = []

    while pos < len(view):
        try:
            chunk, chunk_len = decode_1_chunk(view[pos:])
        except:
            raise Exception(f"chunk: {view[pos:].tobytes()}")

        ret.append(chunk)
        pos += chunk_len

    return ret

def dump(data: bytes, r = None):
    if r is None:
        r = ConsoleRenderer()

    view = memoryview(data)

    chunks = decode_all_chunks(view)

    for ch in chunks:
        ch.render(0, r)
        r.add_newline()

    return r.build_result()



