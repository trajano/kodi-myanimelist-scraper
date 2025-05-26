from typing import Dict, Optional
import xbmc
import xbmcgui
import xbmcplugin
from ._settings import AddOnSettings


def find(
    *,
    plugin_handle: int,
    title: str,
    settings: AddOnSettings,
    year: Optional[str] = None,
):
    """
    https://kodi.wiki/view/Python_tv_scraper_development#Find

    The find action is used for searching for a specific TV show by title and optionally a year that are passed as additional query parameters of the plugin call. This action should use xbmcplugin.addDirectoryItem or xbmcplugin.addDirectoryItems to pass xbmcgui.ListItem instances to Kodi. If only one instance is passed then it is considered as a perfect match. Otherwise the media file won't be matched and will need to be resolved manually by selecting a necessary item from a list. The xbmcgui.ListItem instances must be assigned the following properties:

    label: passed as label parameter to the class constructor. This is the label that is presented to a user during scraping.

    url: passed as url parameter to the class constructor. This should be some unique string that can be used to request all the necessary TV show info from data provider's website or API. It can be, for example, a link to a TV show page on a TV information website or a some unique ID to request TV show information from a REST API.

    thumb (optional): passed via setArtwork() of xbmcgui.ListItem class instance method. This should be a URL of a TV show poster, for example.
    """
    liz = xbmcgui.ListItem(title, "second Title", offscreen=True)
    # The URL here is a "virtual" but does not appear to have any bearing to the real file location. Instead it
    # gets passed to getdetails

    # This would be the
    xbmcplugin.addDirectoryItem(
        handle=plugin_handle,
        url="myanimelist:/anime/30230",
        listitem=liz,
        isFolder=True,
    )


def getdetails(*, plugin_handle: int, settings: AddOnSettings, url: str):
    """
    https://kodi.wiki/view/Python_tv_scraper_development#getdetails
    The getdetails action must pass a single xbmcgui.ListItem via xbmcplugin.setResolvedUrl() function. This action receives url query parameter from the previous stages and should set as much information to the xbmcgui.ListItem instance as possible using appropriate methods. One of the necessary properties that are set via ListItem.setInfo method is episodeguide. This should be some unique string that can be used to retrieve the list of TV show episoded with all the necessary info.
    """
    # fetch the details of the anime
    liz = xbmcgui.ListItem("Demo show 1", offscreen=True)
    tags = liz.getVideoInfoTag()
    tags.setTitle("Demo show 1")
    tags.setOriginalTitle("Demo shåvv 1")
    tags.setSortTitle("2")
    tags.setUserRating(5)
    tags.setPlotOutline("Outline yo")
    tags.setPlot("Plot yo")
    tags.setTagLine("Tag yo")
    tags.setDuration(110)
    tags.setMpaa("T")
    tags.setTrailer("/home/akva/fluffy/bunnies.mkv")
    tags.setGenres(["Action", "Comedy"])
    tags.setWriters(["None", "Want", "To Admit It"])
    tags.setDirectors(["Director 1", "Director 2"])
    tags.setStudios(["Studio1", "Studio2"])
    tags.setDateAdded("2016-01-01")
    tags.setPremiered("2015-01-01")
    tags.setFirstAired("2007-01-01")
    tags.setTvShowStatus("Cancelled")
    # tags.setEpisodeGuide('/path/to/show/guide')
    tags.setEpisodeGuide(f"{url}/episodes")
    tags.setTagLine("Family / Mom <3")
    tags.setRatings({"imdb": (9, 100000), "tvdb": (8.9, 1000)}, defaultrating="imdb")
    tags.setUniqueIDs({"imdb": "tt8938399", "tmdb": "9837493"}, defaultuniqueid="tvdb")
    tags.addSeason(1, "Beautiful")
    tags.addSeason(2, "Sun")
    tags.setCast(
        [
            xbmc.Actor(
                "spiff", "himself", order=2, thumbnail="/home/akva/Pictures/fish.jpg"
            ),
            xbmc.Actor(
                "monkey", "orange", order=1, thumbnail="/home/akva/Pictures/coffee.jpg"
            ),
        ]
    )
    tags.addAvailableArtwork("DefaultBackFanart.png", "banner")
    tags.addAvailableArtwork("/home/akva/Pictures/hawaii-shirt.png", "poster")
    liz.setAvailableFanart(
        [
            {"image": "DefaultBackFanart.png", "preview": "DefaultBackFanart.png"},
            {
                "image": "/home/akva/Pictures/hawaii-shirt.png",
                "preview": "/home/akva/Pictures/hawaii-shirt.png",
            },
        ]
    )
    xbmcplugin.setResolvedUrl(handle=plugin_handle, succeeded=True, listitem=liz)


def getepisodelist(*, plugin_handle: int, settings: AddOnSettings, url: str):
    pass


def getepisodedetails(*, plugin_handle: int, settings: AddOnSettings, url: str):
    pass


def nfourl(*, plugin_handle: int, settings: AddOnSettings, nfo: str):
    pass


def route(params: Dict[str, str], *, plugin_handle: int):
    action = params.get("action")
    if action is None:
        raise ValueError("action is not present in the parameters")
    # look up a function in this module by name
    func = globals().get(action)
    if callable(func):
        # pop off 'action' so func only gets its expected args
        kwargs = {
            k: v for k, v in params.items() if k != "action" and k != "pathSettings"
        }
        settings = AddOnSettings.from_json(params.get("pathSettings") or "{}")
        xbmc.log(f"{action}: {kwargs}", xbmc.LOGWARNING)
        return func(plugin_handle=plugin_handle, settings=settings, **kwargs)
    else:
        xbmc.log(f"unsupported action: {action}", xbmc.LOGWARNING)
