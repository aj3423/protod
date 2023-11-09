from mitmproxy import contentviews
from mitmproxy.addonmanager import Loader

import protod
from protod import Renderer

# Color palettes are defined in:
#   https://github.com/mitmproxy/mitmproxy/blob/746537e0511e0316a144e05e7ba8cc6f6e44768b/mitmproxy/tools/console/palettes.py#L154
class MitmproxyRenderer(Renderer):

    # Long binary data that exceeds `n` bytes are truncated and followed by a '...'
    # use a large value like 1000000 to 'not' truncate
    # default: 32
    def __init__(self, truncate_after = 32):
        self.truncate_after = truncate_after

        """
        It builds a 2D list like:
        [
            [('text', 'white text'), ('offset', 'blue text')],  <-- first line
            [('header', '...'), ('offset', '...')],  <-- second line
            ...
        ]
        """
        self.cells = [[]] 

    def add(self, cell):
        self.cells[len(self.cells)-1].append(cell)
        pass

    def build_result(self):
        # a workaround to remove the trailing `[]` that causes error
        return self.cells[:len(self.cells)-1]

    def add_indent(self, level):
        for _ in range(level):
            self.add(('text', ' ' * 4))

    def add_newline(self):
        self.cells.append([])

    def add_normal(self, s): # white
        self.add(('text', s))

    def add_idtype(self, s): # light red
        self.add(('error', s))

    def add_id(self, s): # light green
        self.add(('replay', s))

    def add_type(self, s): # yellow
        self.add(('alert', s))

    def add_num(self, s): # light cyan
        self.add(('Token_Literal_String', s))

    def add_str(self, s): # light blue
        self.add(('content_media', s))

    def add_bin(self, s): # light yellow
        truncated = s[:self.truncate_after]
        self.add(('warn', ' '.join(format(x, '02x') for x in truncated)))
        if len(s) > self.truncate_after:
            self.add_normal(' ...')


class ViewProto(contentviews.View):
    name = "ViewProto"

    def __call__(self, data, **metadata) -> contentviews.TViewResult:
        return "protobuf decoded", protod.dump(data, MitmproxyRenderer())

    def render_priority(
        self, data: bytes, *, content_type: str | None = None, **metadata
    ) -> float:
        return 1000 if "proto" in content_type else 0

view = ViewProto()

def load(loader: Loader):
    contentviews.add(view)

def done():
    contentviews.remove(view)

