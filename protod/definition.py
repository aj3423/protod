class WireType:
    Varint = 0
    Fixed64 = 1
    Struct = 2
    Deprecated_3 = 3
    Deprecated_4 = 4
    Fixed32 = 5


def wire_type_str(t):
    if t == WireType.Varint:
        return "varint"
    elif t == WireType.Fixed64:
        return "fixed64/double"
    elif t == WireType.Struct:
        return "string"
    elif t == WireType.Fixed32:
        return "fixed32/float"
    else:
        return "Unknown wire type"
