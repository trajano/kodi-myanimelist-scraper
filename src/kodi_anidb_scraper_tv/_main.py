import xml.etree.ElementTree as ET
from datetime import date
import shutil
from kodi_addon import addon_run
from dataclasses import dataclass
from dataclasses_json import (
    dataclass_json,
    Undefined,
    DataClassJsonMixin,
)
from typing import Optional
from kodi_addon.protocols import TvShowScraper
from ._animetitles import load_anime_titles, AnimeTitles
from ._anidburl import AniDbUrl
from ._anidb import AniDb
import time
import xbmcvfs
import re
import xbmcgui
import xbmcplugin


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class AniDbAddOnSettings(DataClassJsonMixin):
    anidb_client_id: str
    anidb_client_version: str
    preferred_language: str
    anidb_last_update: str


FILE_NAME = "special://profile/addon_data/metadata.anidb.tv/anime-titles.xml"


class AniDbScraper(TvShowScraper):
    @staticmethod
    def _clean_title(input: str) -> str:
        input = re.sub(r"\b\[[^\]+?\]\B", "", input)
        return input

    def __init__(self, *, plugin_handle: int, settings: AniDbAddOnSettings):
        self.plugin_handle = plugin_handle
        self.settings = settings
        xbmcvfs.mkdirs("special://profile/addon_data/metadata.anidb.tv")
        # special://profile/addon_data

    def _load_anime_titles_when_needed(self):
        if xbmcvfs.exists(FILE_NAME):
            mtime = xbmcvfs.Stat(FILE_NAME).st_mtime()
            if int(time.time()) - mtime <= 24 * 3600:
                return
        self._load_anime_titles()

    def _load_anime_titles(self):
        with xbmcvfs.File(FILE_NAME, "wb") as output_f, load_anime_titles() as gz:
            shutil.copyfileobj(gz, output_f)

    def find(self, *, title: str, year: Optional[str] = None):
        self._load_anime_titles_when_needed()
        with xbmcvfs.File(FILE_NAME, "rb") as f:
            titles = AnimeTitles(ET.parse(f).getroot())
            for anime in titles.find_all_by_title(title=title):
                for anime_title in anime.titles:
                    liz = xbmcgui.ListItem(anime_title.text, offscreen=True)
                    xbmcplugin.addDirectoryItem(
                        handle=self.plugin_handle,
                        url=AniDbUrl(aid=anime.aid).url,
                        listitem=liz,
                        isFolder=True,
                    )

    def getdetails(self, *, url: str):
        """
        https://kodi.wiki/view/Python_tv_scraper_development#getdetails
        The getdetails action must pass a single xbmcgui.ListItem via xbmcplugin.setResolvedUrl() function. This action receives url query parameter from the previous stages and should set as much information to the xbmcgui.ListItem instance as possible using appropriate methods. One of the necessary properties that are set via ListItem.setInfo method is episodeguide. This should be some unique string that can be used to retrieve the list of TV show episoded with all the necessary info.
        """
        # fetch the details of the anime
        anidb = AniDb(
            client_id=self.settings.anidb_client_id,
            client_version=int(self.settings.anidb_client_version),
        )
        parsed = AniDbUrl.from_url(url)
        anime = anidb.get(parsed.aid)

        liz = xbmcgui.ListItem(
            anime.official_title(self.settings.preferred_language), offscreen=True
        )
        tags = liz.getVideoInfoTag()
        tags.setTitle(anime.official_title(self.settings.preferred_language))
        tags.setOriginalTitle(anime.official_title("ja"))
        tags.setSortTitle(anime.sort_key)
        tags.setPlot(anime.description)
        tags.setEpisodeGuide(AniDbUrl.episode_guide_url)
        tags.setUniqueIDs({"anidb": str(anime.id)}, defaultuniqueid="anidb")

        # tags.setTagLine("Tag yo")
        # tags.setDuration(110)
        # AniDB Doesn't have MPAA the closest is the restricted value.
        if anime.restricted:
            tags.setMpaa("NC-17")

        if anime.mpaa_rating:
            tags.setMpaa(anime.mpaa_rating)
        # tags.setTrailer("/home/akva/fluffy/bunnies.mkv")

        if anime.genres is not None:
            tags.setGenres(anime.genres)
        # tags.setWriters(["None", "Want", "To Admit It"])
        # tags.setDirectors(["Director 1", "Director 2"])
        # if anime.studios is not None:
        #     tags.setStudios([studio.name for studio in anime.studios])
        # # tags.setStudios(["Studio1", "Studio2"])
        tags.setDateAdded(date.today().isoformat())
        if anime.start_date is not None:
            tags.setPremiered(anime.start_date.isoformat())

        # tags.setFirstAired("2007-01-01")ate.isoformat())
        # tags.setFirstAired("2007-01-01")
        # tags.setTvShowStatus(anime.airing_status)
        # tags.setTagLine("Family / Mom <3")
        tags.setRatings(
            {"anidb": (anime.ratings.permanent.mean, anime.ratings.permanent.count)},
            {
                "anidb-temporary": (
                    anime.ratings.temporary.mean,
                    anime.ratings.review.count,
                )
            },
            {"anidb-reviews": (anime.ratings.review.mean, anime.ratings.review.count)},
            defaultrating="anidb",
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
        # if ann_anime is not None:
        #     tags.setEpisodeGuide(
        #         f"animenewsnetwork:/anime/{ann_anime.id}?count={anime.num_episodes}"
        #     )
        #     tags.setUniqueIDs(
        #         {"myanimelist": str(anime_id), "animenewsnetwork": str(ann_anime.id)},
        #         defaultuniqueid="myanimelist",
        #     )
        #     tags.setCast(
        #         [
        #             xbmc.Actor(
        #                 castmember.person,
        #                 castmember.role_label,
        #                 order=castmember.order,
        #             )
        #             for castmember in ann_anime.cast
        #         ]
        #     )
        #     tags.addAvailableArtwork(
        #         ann_anime.picture, arttype="poster", preview=ann_anime.thumbnail
        #     )

        xbmcplugin.setResolvedUrl(
            handle=self.plugin_handle, succeeded=True, listitem=liz
        )


def plugin_main():
    addon_run(addon_cls=AniDbScraper, settings_cls=AniDbAddOnSettings)
