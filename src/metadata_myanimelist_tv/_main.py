from ._settings import AddOnSettings
from ._scraper import MyAnimeListScraper
from kodi_addon import addon_run


def plugin_main():
    addon_run(addon_cls=MyAnimeListScraper, settings_cls=AddOnSettings)
