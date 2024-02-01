from abc import ABC, abstractmethod
from html import escape

from termcolor import colored

from .definition import wire_type_str


# Field formatter and colorizer
class Renderer(ABC):
    # Return the final result, which can be in different formats, eg:
    # for console, it's a string with ansi color
    # for mitmproxy, it's an array of tuple
    @abstractmethod
    def build_result(self):
        pass

    # render repeated fields
    @abstractmethod
    def render_repeated_fields(self, repeated):
        pass

    # render varint
    @abstractmethod
    def render_varint(self, varint):
        pass

    # render fixed32/fixed64
    @abstractmethod
    def render_fixed(self, fixed):
        pass

    # render struct
    @abstractmethod
    def render_struct(self, struct):
        pass


class ConsoleRenderer(Renderer):

    # Long binary data that exceeds `n` bytes is truncated and followed by a '...'
    # use a large value like 1000000 to 'not' truncate
    # default: 32
    def __init__(self, truncate_after=32):
        self.cells = []
        self.truncate_after = truncate_after

    def build_result(self):
        return "".join(self.cells)

    def render_repeated_fields(self, repeated):
        for ch in repeated.items:
            ch.render(self)

    def render_varint(self, varint):
        self._render_idtype(varint.indent_level(), varint.idtype)

        self._add_num(str(varint.i64))
        self._add_normal(" (")
        self._add_num(str(hex(varint.u64)))
        self._add_normal(")")

        self._add_newline()

    def render_fixed(self, fixed):
        self._render_idtype(fixed.indent_level(), fixed.idtype)

        u, i, f = fixed.u, fixed.i, fixed.f

        self._add_normal(str(u))  # show unsigned form
        if i < 0:  # also show signed value if it's negative
            self._add_normal(f" ({str(i)})")

        self._add_normal(f" ({hex(u)}) ({str(f)})")  # show hex and float form
        self._add_newline()

    def render_struct(self, struct):
        self._render_idtype(struct.indent_level(), struct.idtype)

        self._add_normal(f"({str(len(struct.view))}) ")

        if struct.is_str:
            if struct.as_fields:
                if struct.as_str.isprintable():
                    self._render_str(struct.as_str, struct.encoding)
                    self._add_newline()
            else:
                self._render_str(struct.as_str, struct.encoding)

                # Also show hex if:
                # 1. it contains non-printable characters
                # 2. it is short, less than 8 bytes
                if not struct.as_str.isprintable() or 0 < len(struct.view) <= 8:
                    self._add_normal(" (")
                    self._add_bin(struct.view)
                    self._add_normal(")")
                self._add_newline()

        else:
            if not struct.as_fields:
                # show as binary
                self._add_bin(struct.view)
                self._add_newline()

        # 2. show as child struct
        if struct.as_fields:
            self._add_newline()
            for ch in struct.as_fields:
                ch.render(self)

    ###########################

    def _render_idtype(self, indent_level, idtype):
        self._add_indent(indent_level)
        self._add_normal("[")
        self._add_idtype(" ".join(format(x, "02x") for x in idtype.raw_bytes))
        self._add_normal("] ")
        self._add_id(str(idtype.id) + " ")
        self._add_type(wire_type_str(idtype.wire_type))
        self._add_normal(": ")

    def _add_newline(self):
        self._add("\n")

    def _render_str(self, string: str, encoding: str):
        if encoding not in ["ascii"]:
            self._add_normal(f"[{encoding}] ")
        self._add_str(string)

    def _add(self, cell):
        self.cells.append(cell)
        pass

    def _add_indent(self, level):
        self._add(" " * 4 * level)

    def _add_normal(self, s):
        self._add(s)

    def _add_idtype(self, s):
        self._add(colored(s, "light_red"))

    def _add_id(self, s):
        self._add(colored(s, "light_green"))

    def _add_type(self, s):
        self._add(colored(s, "yellow"))

    def _add_num(self, s):
        self._add(colored(s, "light_cyan"))

    def _add_str(self, s):
        self._add(colored(s, "light_blue"))

    def _add_bin(self, s):
        truncated = s[: self.truncate_after]
        self._add(
            colored(" ".join(format(x, "02x") for x in truncated), "light_yellow")
        )
        if len(s) > self.truncate_after:
            self._add_normal(" ...")
