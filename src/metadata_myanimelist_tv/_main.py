import sys
import urllib.parse
import xbmcplugin
import xbmc

from metadata_myanimelist_tv._router import route
from typing import Dict


def _get_params() -> Dict[str, str]:
    # def get_params():
    param_string = sys.argv[2][1:]
    if param_string:
        return dict(urllib.parse.parse_qsl(param_string))
    return {}


def plugin_main():
    params = _get_params()
    plugin_handle = int(sys.argv[1])

    # args ['plugin://metadata.myanimelist.tv/', '575', '?action=find&pathSettings=%7b%7d&title=Foo%203', 'resume:false']
    # params {'action': 'find', 'pathSettings': '{}', 'title': 'Foo 3'}
    xbmc.log(f"params: {params}", xbmc.LOGDEBUG)
    route(params)
    xbmcplugin.endOfDirectory(plugin_handle)
