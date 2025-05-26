import xml.etree.ElementTree as ET
from datetime import date
from typing import Optional
import xbmc
import xbmcgui
import xbmcplugin
from ._settings import AddOnSettings
from ._myanimelist import MyAnimeList
from ._anime_news_network import AnimeNewsNetworkEncyclopedia
from urllib.parse import urlparse, parse_qs
from kodi_addon.protocols import TvShowScraper


class MyAnimeListScraper(TvShowScraper):
    @staticmethod
    def _clean_title(input: str) -> str:
        input = input.replace("[SakuraCircle]", "")
        return input

    def __init__(self, *, plugin_handle: int, settings: AddOnSettings):
        self.plugin_handle = plugin_handle
        self.settings = settings

    def find(
        self,
        *,
        title: str,
        year: Optional[str] = None,
    ):
        """
        https://kodi.wiki/view/Python_tv_scraper_development#Find

        The find action is used for searching for a specific TV show by title and optionally a year that are passed as additional query parameters of the plugin call. This action should use xbmcplugin.addDirectoryItem or xbmcplugin.addDirectoryItems to pass xbmcgui.ListItem instances to Kodi. If only one instance is passed then it is considered as a perfect match. Otherwise the media file won't be matched and will need to be resolved manually by selecting a necessary item from a list. The xbmcgui.ListItem instances must be assigned the following properties:

        label: passed as label parameter to the class constructor. This is the label that is presented to a user during scraping.

        url: passed as url parameter to the class constructor. This should be some unique string that can be used to request all the necessary TV show info from data provider's website or API. It can be, for example, a link to a TV show page on a TV information website or a some unique ID to request TV show information from a REST API.

        thumb (optional): passed via setArtwork() of xbmcgui.ListItem class instance method. This should be a URL of a TV show poster, for example.
        """
        mal = MyAnimeList(self.settings.client_id)
        title = self._clean_title(title)
        if len(title) == 1:
            return
        result = mal.find_anime(title)
        for anime in [item.node for item in result.data]:
            for title in anime.all_titles:
                liz = xbmcgui.ListItem(title, offscreen=True)
                xbmcplugin.addDirectoryItem(
                    handle=self.plugin_handle,
                    url=f"myanimelist:/anime/{anime.id}",
                    listitem=liz,
                    isFolder=True,
                )

    def getdetails(self, *, url: str):
        """
        https://kodi.wiki/view/Python_tv_scraper_development#getdetails
        The getdetails action must pass a single xbmcgui.ListItem via xbmcplugin.setResolvedUrl() function. This action receives url query parameter from the previous stages and should set as much information to the xbmcgui.ListItem instance as possible using appropriate methods. One of the necessary properties that are set via ListItem.setInfo method is episodeguide. This should be some unique string that can be used to retrieve the list of TV show episoded with all the necessary info.
        """
        # fetch the details of the anime
        mal = MyAnimeList(self.settings.client_id)
        parsed = urlparse(url)
        anime_id = int(parsed.path.rsplit("/", 1)[-1])
        anime = mal.get_anime_details(anime_id)
        ann = AnimeNewsNetworkEncyclopedia()
        ann_anime = ann.get_anime(anime.all_titles)
        if ann_anime is None:
            xbmc.log(
                f"Unable to determine anime from Anime News Network {anime.all_titles}.  No episode details will be available",
                xbmc.LOGWARNING,
            )
        liz = xbmcgui.ListItem(anime.title, offscreen=True)
        tags = liz.getVideoInfoTag()
        tags.setTitle(anime.get_title(self.settings.preferred_language))
        tags.setOriginalTitle(anime.original_title)
        # tags.setSortTitle("2")
        # tags.setUserRating(anime.mean)
        tags.setPlot(anime.synopsis)
        if anime.background:
            tags.setTagLine(anime.background)
        tags.setEpisodeGuide(f"{url}/episodes?count={anime.num_episodes}")
        tags.setUniqueIDs({"myanimelist": str(anime_id)}, defaultuniqueid="myanimelist")

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

        # tags.setFirstAired("2007-01-01")ate.isoformat())
        # tags.setFirstAired("2007-01-01")
        tags.setTvShowStatus(anime.airing_status)
        # tags.setTagLine("Family / Mom <3")
        tags.setRatings(
            {"myanimelist": (anime.mean, anime.num_scoring_users)},
            defaultrating="myanimelist",
        )
        # tags.setRatings({"imdb": (9, 100000), "tvdb": (8.9, 1000)}, defaultrating="imdb")
        # tags.addSeason(1, "Beautiful")
        # tags.addSeason(2, "Sun")
        # tags.setCast(
        #     [
        #         xbmc.Actor(
        #             "spiff", "himself", order=2, thumbnail="/home/akva/Pictures/fish.jpg"
        #         ),
        #         xbmc.Actor(
        #             "monkey", "orange", order=1, thumbnail="/home/akva/Pictures/coffee.jpg"
        #         ),
        #     ]
        # )
        tags.addAvailableArtwork(
            anime.main_picture.url, arttype="poster", preview=anime.main_picture.medium
        )
        if anime.pictures is not None:
            for picture in anime.pictures:
                tags.addAvailableArtwork(
                    picture.url, arttype="poster", preview=anime.main_picture.medium
                )
        # tags.addAvailableArtwork("DefaultBackFanart.png", "banner")
        # tags.addAvailableArtwork("/home/akva/Pictures/hawaii-shirt.png", "poster")
        # liz.setAvailableFanart(
        #     [
        #         {"image": "DefaultBackFanart.png", "preview": "DefaultBackFanart.png"},
        #         {
        #             "image": "/home/akva/Pictures/hawaii-shirt.png",
        #             "preview": "/home/akva/Pictures/hawaii-shirt.png",
        #         },
        #     ]
        # )
        if ann_anime is not None:
            tags.setEpisodeGuide(
                f"animenewsnetwork:/anime/{ann_anime.id}?count={anime.num_episodes}"
            )
            tags.setUniqueIDs(
                {"myanimelist": str(anime_id), "animenewsnetwork": str(ann_anime.id)},
                defaultuniqueid="myanimelist",
            )
            tags.setCast(
                [
                    xbmc.Actor(
                        castmember.person,
                        castmember.role_label,
                        order=castmember.order,
                    )
                    for castmember in ann_anime.cast
                ]
            )
            tags.addAvailableArtwork(
                ann_anime.picture, arttype="poster", preview=ann_anime.thumbnail
            )

        xbmcplugin.setResolvedUrl(
            handle=self.plugin_handle, succeeded=True, listitem=liz
        )

    def getepisodelist(self, *, url: str):
        parsed = urlparse(url)
        if parsed.scheme == "myanimelist":
            segments = parsed.path.strip("/").split("/")
            anime_id = int(segments[1])
            episode_count = int(parse_qs(parsed.query).get("count", [0])[0])
            for i in range(1, episode_count + 1):
                liz = xbmcgui.ListItem(f"Episode {i}", offscreen=True)
                tags = liz.getVideoInfoTag()
                tags.setTitle(f"Episode {i}")
                tags.setSeason(1)
                tags.setEpisode(i)
                xbmcplugin.addDirectoryItem(
                    handle=self.plugin_handle,
                    url=f"myanimelist:/anime/{anime_id}/episode/{i}",
                    listitem=liz,
                    isFolder=False,
                )

        elif parsed.scheme == "animenewsnetwork":
            anime_id = int(parsed.path.rsplit("/", 1)[-1])
            ann = AnimeNewsNetworkEncyclopedia()
            anime = ann.get_anime_by_id(anime_id)
            episode_count = int(parse_qs(parsed.query).get("count", [0])[0])
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
                    handle=self.plugin_handle,
                    url=f"animenewsnetwork:/anime/{anime_id}/episode/{episode.number}",
                    listitem=liz,
                    isFolder=False,
                )
            for i in range(len(anime.episodes), episode_count + 1):
                liz = xbmcgui.ListItem(f"Episode {i}", offscreen=True)
                tags = liz.getVideoInfoTag()
                tags.setTitle(f"Episode {i}")
                tags.setSeason(1)
                tags.setEpisode(i)
                xbmcplugin.addDirectoryItem(
                    handle=self.plugin_handle,
                    url=f"myanimelist:/anime/{anime_id}/episode/{i}",
                    listitem=liz,
                    isFolder=False,
                )

    def getepisodedetails(self, *, url: str):
        parsed = urlparse(url)
        if parsed.scheme == "myanimelist":
            episode_num = int(parsed.path.rsplit("/", 1)[-1])
            liz = xbmcgui.ListItem(f"Episode {episode_num}", offscreen=True)
            tags = liz.getVideoInfoTag()
            tags.setTitle(f"Episode {episode_num}")
            tags.setSeason(1)
            tags.setEpisode(episode_num)
            tags.setDateAdded(date.today().isoformat())
            xbmcplugin.setResolvedUrl(
                handle=self.plugin_handle, succeeded=True, listitem=liz
            )
        if parsed.scheme == "animenewsnetwork":
            segments = parsed.path.strip("/").split("/")
            anime_id = int(segments[1])
            episode_num = int(parsed.path.rsplit("/", 1)[-1])
            liz = xbmcgui.ListItem(f"Episode {episode_num}", offscreen=True)
            ann = AnimeNewsNetworkEncyclopedia()
            anime = ann.get_anime_by_id(anime_id)
            title = f"Episode {episode_num}"
            if anime is not None:
                episode = anime.get_episode(episode_num)
                if episode is not None:
                    title = episode.title
            tags = liz.getVideoInfoTag()
            tags.setTitle(title)
            tags.setSeason(1)
            tags.setEpisode(episode_num)
            tags.setDateAdded(date.today().isoformat())
            xbmcplugin.setResolvedUrl(
                handle=self.plugin_handle, succeeded=True, listitem=liz
            )

    def nfourl(self, *, nfo: str):
        nfo_xml = ET.fromstring(nfo)
        xbmc.log(f"{nfo_xml}", level=xbmc.LOGWARNING)

    def getartwork(self, *, id: str):
        liz = xbmcgui.ListItem(f"artwork {id}", offscreen=True)
        mal = MyAnimeList(self.settings.client_id)
        anime = mal.get_anime_details(int(id))
        tags = liz.getVideoInfoTag()
        tags.setTitle("My Anime List Main Picture")
        tags.addAvailableArtwork(
            anime.main_picture.url, arttype="poster", preview=anime.main_picture.medium
        )
        xbmc.log(f"{anime.main_picture.url}", xbmc.LOGWARNING)
        xbmcplugin.setResolvedUrl(
            handle=self.plugin_handle, succeeded=True, listitem=liz
        )
