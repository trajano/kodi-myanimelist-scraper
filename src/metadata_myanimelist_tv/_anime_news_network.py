from dataclasses import dataclass
import xml.etree.ElementTree as ET
from typing import Iterable, Optional, List
from requests import get
import time


@dataclass
class AnimeNewsNetworkTitle:
    lang: str
    text: str

    def __init__(self, el: ET.Element):
        self.lang = el.attrib["lang"]
        self.text = el.text or ""


@dataclass
class AnimeNewsNetworkEpisode:
    number: int
    titles: List[AnimeNewsNetworkTitle]

    def __init__(self, el: ET.Element):
        self.number = int(el.attrib["num"])
        self.titles = []
        for title_element in el.iter("title"):
            self.titles.append(AnimeNewsNetworkTitle(title_element))

    @property
    def title(self) -> str:
        return self.titles[0].text


@dataclass
class AnimeNewsNetworkEncyclopediaEntry:
    id: int
    name: str
    type: str
    precision: str
    episodes: List[AnimeNewsNetworkEpisode]

    # this is not a json
    def __init__(self, el: ET.Element):
        self.el = el
        self.name = el.attrib["name"]
        self.type = el.attrib["type"]
        self.id = int(el.attrib["id"])
        self.precision = el.attrib["precision"]
        self.episodes = []
        for info_element in el.iter("info"):
            # Extract the pictures
            pass
        for episode_element in el.iter("episode"):
            self.episodes.append(AnimeNewsNetworkEpisode(episode_element))

    def get_episode(self, episode_num) -> Optional[AnimeNewsNetworkEpisode]:
        return next((ep for ep in self.episodes if ep.number == episode_num), None)


class AnimeNewsNetworkEncyclopedia:
    def get_anime(
        self, titles: Iterable[str]
    ) -> Optional[AnimeNewsNetworkEncyclopediaEntry]:
        """
        Get anime from encyclopedia API.

        This will do a search on the encyclopedia with the given titles.
        The XML is scanned for the first exact matching title in the titles list.
        """
        params = [("anime", f"~{t}") for t in titles]
        response = get("https://cdn.animenewsnetwork.com/encyclopedia/api.xml", params)
        # Always sleep for 1 second
        time.sleep(1.0)
        root = ET.fromstring(response.content)
        # Figure out what to do with precision later
        for anime_element in root.iter("anime"):
            name = anime_element.attrib["name"]
            if name is None:
                continue
            if name in titles:
                return AnimeNewsNetworkEncyclopediaEntry(anime_element)
        return None

    def get_anime_by_id(self, id: int) -> Optional[AnimeNewsNetworkEncyclopediaEntry]:
        """
        Get anime from encyclopedia API.

        This will do a search on the encyclopedia with the given titles.
        The XML is scanned for the first exact matching title in the titles list.
        """
        response = get(
            "https://cdn.animenewsnetwork.com/encyclopedia/api.xml", {"anime": str(id)}
        )
        # Always sleep for 1 second
        time.sleep(1.0)
        root = ET.fromstring(response.content)
        # Figure out what to do with precision later
        for anime_element in root.iter("anime"):
            return AnimeNewsNetworkEncyclopediaEntry(anime_element)
        return None

    def find_anime_id(self, titles: Iterable[str]) -> Optional[int]:
        """
        Find the anime ID.

        This will do a search on the encyclopedia with the given titles.
        The XML is scanned for the first exact matching title in the titles list.
        """
        params = [("anime", f"~{t}") for t in titles]
        response = get("https://cdn.animenewsnetwork.com/encyclopedia/api.xml", params)
        # Always sleep for 1 second
        time.sleep(1.0)
        root = ET.fromstring(response.content)
        # Figure out what to do with precision later
        for anime_element in root.iter("anime"):
            name = anime_element.attrib["name"]
            if name is None:
                continue
            if name in titles:
                return AnimeNewsNetworkEncyclopediaEntry(anime_element).id
        return None
