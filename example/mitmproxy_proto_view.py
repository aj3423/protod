from mitmproxy import contentviews, ctx
from mitmproxy.addonmanager import Loader

import protod
from protod import ConsoleRenderer


# Color palettes are defined in:
#  https://github.com/mitmproxy/mitmproxy/blob/746537e0511e0316a144e05e7ba8cc6f6e44768b/mitmproxy/tools/console/palettes.py#L154
class MitmproxyRenderer(ConsoleRenderer):

    # Long binary data that exceeds `n` bytes are truncated and followed by a '...'
    # use a large value like 1000000 to 'not' truncate
    # default: 32
    def __init__(self, truncate_after=32):
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

    def _add_newline(self):
        self.cells.append([])

    def build_result(self):
        # a workaround to remove the trailing `[]` that causes error
        return self.cells[: len(self.cells) - 1]

    def _add(self, cell):
        self.cells[len(self.cells) - 1].append(cell)
        pass

    def _add_indent(self, level):
        for _ in range(level):
            self._add(("text", " " * 4))

    def _add_normal(self, s):  # white
        self._add(("text", s))

    def _add_idtype(self, s):  # light red
        self._add(("error", s))

    def _add_id(self, s):  # light green
        self._add(("replay", s))

    def _add_type(self, s):  # yellow
        self._add(("alert", s))

    def _add_num(self, s):  # light cyan
        self._add(("Token_Literal_String", s))

    def _add_str(self, s):  # light blue
        self._add(("content_media", s))

    def _add_bin(self, s):  # light yellow
        truncated = s[: self.truncate_after]
        self._add(("warn", " ".join(format(x, "02x") for x in truncated)))
        if len(s) > self.truncate_after:
            self._add_normal(" ...")


class ViewProto(contentviews.View):
    name = "ViewProto"

    def __call__(self, data, **metadata) -> contentviews.TViewResult:
        # ctx.log.error("111111")
        # try:
        #     protod.dump(data, renderer=MitmproxyRenderer())
        # except Exception as e:
        #     ctx.log.error(e)
        return "protobuf decoded", protod.dump(data, renderer=MitmproxyRenderer())

    def render_priority(
        self, data: bytes, *, content_type: str | None = None, **metadata
    ) -> float:
        return 1000 if "proto" in content_type else 0


view = ViewProto()


def load(loader: Loader):
    contentviews.add(view)


def done():
    contentviews.remove(view)
