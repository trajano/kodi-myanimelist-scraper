import sys
import urllib.parse
import xbmc
import xbmcplugin
# from metadata_myanimelist_tv import route


#def get_params() -> dict[str, str]:
def get_params():
    param_string = sys.argv[2][1:]
    if param_string:
        return dict(urllib.parse.parse_qsl(param_string))
    return {}


print(__name__)
params = get_params()
plugin_handle = int(sys.argv[1])
action = params.get("action")


print(params)
print(params)
print(params)
print(params)
print(params)
print(params)
print(params)
print(params)
print(params)
print(params)
print(params)
print(params)
print(params)
print(params)
print(params)
print(params)
print(params)
print(params)
xbmc.log(f"args {sys.argv}")
xbmc.log(f"params {params}")
# route(params)
xbmcplugin.endOfDirectory(plugin_handle)
