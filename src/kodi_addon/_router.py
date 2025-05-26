import sys
import urllib.parse
import xbmcplugin
import xbmc
from typing import Dict, Type
from .protocols import KodiAddon
from dataclasses_json import DataClassJsonMixin


def _get_params() -> Dict[str, str]:
    param_string = sys.argv[2][1:]
    if param_string:
        return dict(urllib.parse.parse_qsl(param_string))
    return {}


def _route(
    params: Dict[str, str],
    *,
    plugin_handle: int,
    scraper_cls: Type[KodiAddon],
    settings_cls: Type[DataClassJsonMixin],
):
    action = params.get("action")
    if action is None:
        raise ValueError("action is not present in the parameters")
    action = action.lower()

    settings = settings_cls.from_json(params.get("pathSettings") or "{}")
    scraper = scraper_cls(plugin_handle=plugin_handle, settings=settings)
    # look up a function in this module by name
    func = getattr(scraper, action)
    if callable(func):
        # pop off 'action' and 'pathSettings' so func only gets its expected args
        kwargs = {
            k: v for k, v in params.items() if k != "action" and k != "pathSettings"
        }
        xbmc.log(f"{action}: {kwargs}", xbmc.LOGDEBUG)
        func(**kwargs)
    else:
        xbmc.log(f"unsupported action: {action} {params}", xbmc.LOGWARNING)


def addon_run(addon_cls: Type[KodiAddon], settings_cls: Type[DataClassJsonMixin]):
    params = _get_params()
    plugin_handle = int(sys.argv[1])
    xbmc.log(f"params: {params}", xbmc.LOGDEBUG)
    _route(
        params,
        plugin_handle=plugin_handle,
        scraper_cls=addon_cls,
        settings_cls=settings_cls,
    )
    xbmcplugin.endOfDirectory(plugin_handle)
