import sys
import urllib.parse
import xbmcplugin

from .router import route
from typing import Dict


def get_params() -> Dict[str, str]:
    # def get_params():
    param_string = sys.argv[2][1:]
    if param_string:
        return dict(urllib.parse.parse_qsl(param_string))
    return {}


if __name__ == "__main__":
    params = get_params()
    plugin_handle = int(sys.argv[1])
    action = params.get("action")

    # __name__ == __main__
    # args ['plugin://metadata.myanimelist.tv/', '575', '?action=find&pathSettings=%7b%7d&title=Foo%203', 'resume:false']
    # params {'action': 'find', 'pathSettings': '{}', 'title': 'Foo 3'}
    route(params)
    xbmcplugin.endOfDirectory(plugin_handle)
