import sys
import urllib.parse

import xbmcplugin


def get_params():
    param_string = sys.argv[2][1:]
    if param_string:
        return dict(urllib.parse.parse_qsl(param_string))
    return {}


params = get_params()
plugin_handle = int(sys.argv[1])
action = params.get("action")
xbmcplugin.endOfDirectory(plugin_handle)
