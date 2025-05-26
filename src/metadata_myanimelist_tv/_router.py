from datetime import date
from typing import Dict, Optional
import xbmc
import xbmcgui
import xbmcplugin
from ._settings import AddOnSettings
from ._myanimelist import MyAnimeList
from ._anime_news_network import AnimeNewsNetworkEncyclopedia

from urllib.parse import urlparse


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
    mal = MyAnimeList(settings.client_id)
    result = mal.find_anime(title)
    for anime in [item.node for item in result.data]:
        liz = xbmcgui.ListItem(anime.title, "", offscreen=True)
        xbmcplugin.addDirectoryItem(
            handle=plugin_handle,
            url=f"myanimelist:/anime/{anime.id}",
            listitem=liz,
            isFolder=True,
        )


def getdetails(*, plugin_handle: int, settings: AddOnSettings, url: str):
    """
    https://kodi.wiki/view/Python_tv_scraper_development#getdetails
    The getdetails action must pass a single xbmcgui.ListItem via xbmcplugin.setResolvedUrl() function. This action receives url query parameter from the previous stages and should set as much information to the xbmcgui.ListItem instance as possible using appropriate methods. One of the necessary properties that are set via ListItem.setInfo method is episodeguide. This should be some unique string that can be used to retrieve the list of TV show episoded with all the necessary info.
    """
    # fetch the details of the anime
    mal = MyAnimeList(settings.client_id)
    parsed = urlparse(url)
    anime_id = int(parsed.path.rsplit("/", 1)[-1])
    anime = mal.get_anime_details(anime_id)
    ann = AnimeNewsNetworkEncyclopedia()
    ann_anime = ann.get_anime(anime.all_titles)
    liz = xbmcgui.ListItem(anime.title, offscreen=True)
    tags = liz.getVideoInfoTag()
    tags.setTitle(anime.title)
    tags.setOriginalTitle(anime.original_title)
    # tags.setSortTitle("2")
    # tags.setUserRating(anime.mean)
    tags.setPlotOutline(anime.synopsis)
    if ann_anime is None:
        xbmc.log(
            f"Unable to determine anime from Anime News Network {anime.all_titles}.  No episode data will be available",
            xbmc.LOGWARNING,
        )
        tags.setUniqueIDs({"myanimelist": str(anime_id)}, defaultuniqueid="myanimelist")
    else:
        tags.setEpisodeGuide(f"{url}/episodes/{ann_anime.id}")
        tags.setUniqueIDs(
            {"myanimelist": str(anime_id), "animenewsnetwork": str(ann_anime.id)},
            defaultuniqueid="myanimelist",
        )

    # tags.setPlot("Plot yo")
    # tags.setTagLine("Tag yo")
    # tags.setDuration(110)
    tags.setMpaa(anime.mpaa_rating)
    # tags.setTrailer("/home/akva/fluffy/bunnies.mkv")

    if anime.genres is not None:
        tags.setGenres([genre.name for genre in anime.genres])
    tags.setWriters(["None", "Want", "To Admit It"])
    tags.setDirectors(["Director 1", "Director 2"])
    if anime.studios is not None:
        tags.setStudios([studio.name for studio in anime.studios])
    # tags.setStudios(["Studio1", "Studio2"])
    tags.setDateAdded(date.today().isoformat())
    if anime.start_date is not None:
        tags.setPremiered(anime.start_date.isoformat())
    # tags.setFirstAired("2007-01-01")
    tags.setTvShowStatus(anime.airing_status)
    # tags.setTagLine("Family / Mom <3")
    tags.setRatings({"myanimelist": (anime.mean, 1000)}, defaultrating="myanimelist")
    # tags.setRatings({"imdb": (9, 100000), "tvdb": (8.9, 1000)}, defaultrating="imdb")
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
    parsed = urlparse(url)
    anime_id = int(parsed.path.rsplit("/", 1)[-1])
    ann = AnimeNewsNetworkEncyclopedia()
    anime = ann.get_anime_by_id(anime_id)
    if anime is None:
        xbmc.log(
            f"Unable to determine anime from Anime News Network id={anime_id}",
            xbmc.LOGERROR,
        )
        return
    for episode in anime.episodes:
        liz = xbmcgui.ListItem(episode.title, offscreen=True)
        tags = liz.getVideoInfoTag()
        tags.setTitle(episode.title)
        tags.setSeason(1)
        tags.setEpisode(episode.number)
        # tags.setFirstAired('2015-01-01')
        # tags.addAvailableArtwork('/path/to/episode1', 'banner')
        xbmcplugin.addDirectoryItem(
            handle=plugin_handle,
            url=f"ann:/anime/{anime_id}/episode/{episode.number}",
            listitem=liz,
            isFolder=False,
        )


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
