from protod import ConsoleRenderer


# The HtmlRenderer builds a full html div string,
# which can be simply set to a <div>
#
# usage:
#
#  html_tag = protod.dump(proto, protod.HtmlRenderer())
#  send the html_tag to client browser
#  $('#div').text(html_tag)
#
class HtmlRenderer(ConsoleRenderer):

    def _add_indent(self, level):
        self._add("&nbsp;" * 4 * level)

    def _add_newline(self):
        self._add("</br>")

    def _add_normal(self, s):
        self._add(s)

    def _add_idtype(self, s):
        self._add(f"<font color='#ff2200'>{s}</font>")

    def _add_id(self, s):
        self._add(f"<font color='#00ff11'>{s}</font>")

    def _add_type(self, s):
        self._add(f"<font color='#808000'>{s}</font>")

    def _add_num(self, s):
        self._add(f"<font color='cyan'>{s}</font>")

    def _add_str(self, s):
        self._add(f"<font color='blue'>{escape(s)}</font>")

    def _add_bin(self, s):
        self._add(
            f"<font color='yellow'>{escape(' '.join(format(x, '02x') for x in s))}</font>"
        )
