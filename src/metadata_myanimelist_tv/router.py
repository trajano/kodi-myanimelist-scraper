from typing import Dict
import xbmc


def find(*, title: str, pathSettings: str, year: str | None):
    pass


def getdetails(*, url: str):
    pass


def getepisodelist(*, url: str):
    pass


def getepisodedetails(*, url: str):
    pass


def nfourl(*, nfo: str):
    pass


def route(params: Dict[str, str]):
    action = params.get("action")
    if action is None:
        raise ValueError("action is not present in the parameters")
    # look up a function in this module by name
    func = globals().get(action)
    if callable(func):
        # pop off 'action' so func only gets its expected args
        kwargs = {k: v for k, v in params.items() if k != "action"}
        return func(**kwargs)
    else:
        xbmc.log(f"unsupported action: {action}", xbmc.LOGWARNING)
