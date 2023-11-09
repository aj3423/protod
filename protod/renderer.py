from abc import ABC, abstractmethod
from html import escape

from termcolor import colored

# Chunk formatter and colorizer
class Renderer(ABC):

    # Add an cell to the final result
    @abstractmethod
    def add(self, cell):
        pass

    # Return the final result, which can be in different formats, eg:
    # for console, it's a string with ansi color
    # for mitmproxy, it's an array of tuple
    @abstractmethod
    def build_result(self):
        pass

    # normal white cell
    @abstractmethod
    def add_normal(self, s:str):
        pass

    # the indent character like '\t' or '&nbsp;'
    @abstractmethod
    def add_indent(self, level: int):
        pass

    # add a newline
    @abstractmethod
    def add_newline(self):
        pass

    # add the bytes that contain both proto field id and wire type
    @abstractmethod
    def add_idtype(self, s: str):
        pass

    # add proto field id
    @abstractmethod
    def add_id(self, s: str):
        pass

    # add proto field type
    @abstractmethod
    def add_type(self, s: str):
        pass

    # add numbers
    @abstractmethod
    def add_num(self, s: str):
        pass

    # add strings
    @abstractmethod
    def add_str(self, s: str):
        pass

    # add binary bytes
    @abstractmethod
    def add_bin(self, s: memoryview):
        pass

class ConsoleRenderer(Renderer):

    # Long binary data that exceeds `n` bytes are truncated and followed by a '...' 
    # use a large value like 1000000 to 'not' truncate
    # default: 32
    def __init__(self, truncate_after = 32):
        self.cells = [] 
        self.truncate_after = truncate_after

    def add(self, cell):
        self.cells.append(cell)
        pass

    def build_result(self):
        return ''.join(self.cells)

    def add_indent(self, level):
        for _ in range(level):
            self.add(' ' * 4)

    def add_newline(self):
        self.add("\n")

    def add_normal(self, s):
        self.add(s)

    def add_idtype(self, s):
        self.add(colored(s, "light_red"))

    def add_id(self, s):
        self.add(colored(s, "light_green"))

    def add_type(self, s):
        self.add(colored(s, "yellow"))

    def add_num(self, s):
        self.add(colored(s, "light_cyan"))

    def add_str(self, s):
        self.add(colored(s, "light_blue"))

    def add_bin(self, s):
        truncated = s[:self.truncate_after]
        self.add(colored(' '.join(format(x, '02x') for x in truncated), "light_yellow"))
        if len(s) > self.truncate_after:
            self.add_normal(' ...')


# The HtmlRenderer builds a full html div string, 
# which can be simply set to a <div>
class HtmlRenderer(Renderer):

    def __init__(self):
        self.cells = [] 

    def add(self, cell):
        self.cells.append(cell)
        pass

    def build_result(self):
        return ''.join(self.cells)

    def add_indent(self, level):
        for _ in range(level):
            self.add("&nbsp;" * 4)

    def add_newline(self):
        self.add("</br>")

    def add_normal(self, s):
        self.add(s)

    def add_idtype(self, s):
        self.add(f"<font color='#ff2200'>{s}</font>")

    def add_id(self, s):
        self.add(f"<font color='#00ff11'>{s}</font>")

    def add_type(self, s):
        self.add(f"<font color='#808000'>{s}</font>")

    def add_num(self, s):
        self.add(f"<font color='cyan'>{s}</font>")

    def add_str(self, s):
        self.add(f"<font color='blue'>{escape(s)}</font>")

    def add_bin(self, s):
        self.add(f"<font color='yellow'>{escape(' '.join(format(x, '02x') for x in s))}</font>")


