from typing import Dict
import xbmc


def find(*, title: str, pathSettings: str):
    pass


def route(params: Dict[str, str]):
    action = params.get("action")
    if action is None:
        raise ValueError("action is not present in the parameters")
    elif action == "find":
        find(**params)
    else:
        xbmc.log(f"unsupported action: {action}", xbmc.LOGWARNING)
