import sys
import urllib.parse

import xbmcplugin
from metadata_myanimelist_tv import route


def get_params() -> dict[str, str]:
    param_string = sys.argv[2][1:]
    if param_string:
        return dict(urllib.parse.parse_qsl(param_string))
    return {}


params = get_params()
plugin_handle = int(sys.argv[1])
action = params.get("action")
route(params)
xbmcplugin.endOfDirectory(plugin_handle)
