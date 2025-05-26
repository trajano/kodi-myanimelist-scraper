from typing import Dict
import xbmc
from ._settings import AddOnSettings
from ._scraper import MyAnimeListScraper


def route(params: Dict[str, str], *, plugin_handle: int):
    action = params.get("action")
    if action is None:
        raise ValueError("action is not present in the parameters")
    action = action.lower()

    settings = AddOnSettings.from_json(params.get("pathSettings") or "{}")
    scraper = MyAnimeListScraper(plugin_handle=plugin_handle, settings=settings)
    # look up a function in this module by name
    func = getattr(scraper, action)
    if callable(func):
        # pop off 'action' and 'pathSettings' so func only gets its expected args
        kwargs = {
            k: v for k, v in params.items() if k != "action" and k != "pathSettings"
        }
        xbmc.log(f"{action}: {kwargs}", xbmc.LOGDEBUG)
        return func(**kwargs)
    else:
        xbmc.log(f"unsupported action: {action} {params}", xbmc.LOGWARNING)
