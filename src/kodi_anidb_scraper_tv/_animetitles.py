from difflib import SequenceMatcher
import xml.etree.ElementTree as ET
from dataclasses import dataclass
import cloudscraper
from typing import Optional, List
from gzip import GzipFile
from pathlib import Path
from ._anidb import AniDbTitle


def load_anime_titles(
    gz_download_path: Optional[str] = None, anidb_proxy: Optional[str] = None
) -> GzipFile:
    base_url = anidb_proxy or "https://anidb.net"
    if gz_download_path is not None:
        download_path = Path(gz_download_path)
        if not download_path.exists():
            scraper = cloudscraper.create_scraper(browser="chrome")
            response = scraper.get(f"{base_url}/api/anime-titles.xml.gz", stream=True)
            response.raise_for_status()
            with download_path.open("wb") as gz:
                gz.write(response.content)
        return GzipFile(fileobj=download_path.open("rb"))

    scraper = cloudscraper.create_scraper(browser="chrome")
    response = scraper.get(f"{base_url}/api/anime-titles.xml.gz", stream=True)
    response.raise_for_status()
    return GzipFile(fileobj=response.raw)


@dataclass
class AnimeTitleAnime:
    aid: int
    titles: List[AniDbTitle]

    def __init__(self, el: ET.Element):
        self.aid = int(el.attrib["aid"])
        self.titles = []
        for title_element in el.iter("title"):
            self.titles.append(AniDbTitle(title_element))

    def official_title(self, lang: str) -> str:
        # try official in requested lang, then Japanese, then English
        for current_lang in (lang, "ja", "en"):
            title = next(
                (
                    t.text
                    for t in self.titles
                    if t.is_official and t.lang == current_lang
                ),
                None,
            )
            if title:
                return title
        # fallback to any main title
        return next((t.text for t in self.titles if t.is_main), "")

    @property
    def sort_key(self) -> str:
        return next((t.text for t in self.titles if t.title_type == "main")).lower()


@dataclass
class AnimeTitles:
    animes: List[AnimeTitleAnime]

    def __init__(self, el: ET.Element):
        self.animes = []
        for anime_element in el.iter("anime"):
            self.animes.append(AnimeTitleAnime(anime_element))

    def find_all_by_title(self, title: str, fuzz=0.8) -> List[AnimeTitleAnime]:
        title_lower = title.lower()

        exact = [
            anime
            for anime in self.animes
            if any(t.lower == title_lower for t in anime.titles)
        ]
        if exact:
            return exact

        substr = [
            anime
            for anime in self.animes
            if any(title_lower in t.lower for t in anime.titles)
        ]
        if substr:
            return substr

        def fuzzy_match(a: str, b: str) -> bool:
            return SequenceMatcher(None, a.lower(), b.lower()).ratio() > fuzz

        fuzzy = [
            anime
            for anime in self.animes
            if any(fuzzy_match(title, t.text) for t in anime.titles)
        ]
        return fuzzy
