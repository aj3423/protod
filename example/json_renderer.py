import binascii
import json

import protod
from protod import Renderer


class JsonRenderer(Renderer):

    def __init__(self):
        self.result = dict()
        self.current = self.result

    def _add(self, id, item):
        self.current[id] = item

    def _build_tmp_item(self, chunk):
        # use a temporary renderer to build
        jr = JsonRenderer()
        chunk.render(jr)
        tmp_dict = jr.build_result()

        # the tmp_dict only contains 1 item
        for _, item in tmp_dict.items():
            return item

    def build_result(self):
        return self.result

    def render_repeated_fields(self, repeated):
        arr = []
        for ch in repeated.items:
            arr.append(self._build_tmp_item(ch))
        self._add(repeated.idtype.id, arr)

    def render_varint(self, varint):
        self._add(varint.idtype.id, varint.i64)

    def render_fixed(self, fixed):
        self._add(fixed.idtype.id, fixed.i)

    def render_struct(self, struct):

        curr = None

        if struct.as_fields:
            curr = {}
            for ch in struct.as_fields:
                curr[ch.idtype.id] = self._build_tmp_item(ch)
        elif struct.is_str:
            curr = struct.as_str

        else:
            curr = " ".join(format(x, "02x") for x in struct.view)

        self._add(struct.idtype.id, curr)


# return (
#   decoded bytes: bytes
#   encoding name: str
#   decoding succeeded: bool
# )
def decode_utf8(view) -> tuple[bytes, str, bool]:
    view_bytes = view.tobytes()
    try:
        utf8 = "UTF-8"
        decoded = view_bytes.decode(utf8)
        return decoded, utf8, True
    except:
        return view_bytes, "", False


sample = "0885ffffffffffffffff011084461a408d17480ac969d3d8fd619e9bc10870688d17480ac969d3d8fd619e9bc10870688d17480ac969d3d8fd619e9bc10870688d17480ac969d3d8fd619e9bc10870682a281d8fc2e842213333333333f34340a2061767656f67726170686963616c20636f6f7264696e617465321b57696e6e69c3a9c3a9c3a9c3a9207468c3a9204469637461746f723208bab8b4d9c0dbc0bd3210c4e3b5c4c3e6b3a3c4e3b5c4c3e6b3a3323ca16dae61bb79a16ea4eaa147a175a767a46ca4a3b3d5a141acb0a8e4addda6e6b463b944ac47a45da143a176a16dbdd7bb79a16ea4aaa147a175a4a3322d8366834283588376838c8343838226233132393b5b836882aa26233134343bdd92e882c582ab82dc82b982f12e"

proto_bytes = binascii.unhexlify(sample)

ret = protod.dump(
    proto_bytes,
    renderer=JsonRenderer(),
    str_decoder=decode_utf8,
)
print(json.dumps(ret, indent=4, ensure_ascii=False))
