from dataclasses import dataclass
from dataclasses_json import dataclass_json, Undefined, CatchAll
from requests import get
from typing import List, Optional


@dataclass_json
@dataclass
class MyAnimeListPicture:
    medium: str
    large: Optional[str]

    def url(self) -> str:
        return self.large or self.medium


@dataclass_json
@dataclass
class MyAnimeListGenre:
    id: int
    name: str


@dataclass_json
@dataclass
class MyAnimeListStudio:
    id: int
    name: str


@dataclass_json(undefined=Undefined.INCLUDE)
@dataclass
class MyAnimeListAlternativeTitles:
    synonyms: List[str]
    titles: CatchAll


@dataclass_json
@dataclass
class MyAnimeListAnime:
    id: int
    title: str
    main_picture: MyAnimeListPicture
    synopsis: Optional[str]
    start_date: Optional[str]
    mean: Optional[float]
    genres: Optional[List[MyAnimeListGenre]]
    num_episodes: Optional[int]
    rating: Optional[str]
    studios: Optional[List[MyAnimeListStudio]]
    pictures: Optional[List[MyAnimeListPicture]]
    background: Optional[str]
    alternative_titles: Optional[MyAnimeListAlternativeTitles]


class MyAnimeList:
    def __init__(self, client_id: str) -> None:
        self.client_id = client_id

    def find_anime(self, query: str, *, limit=100, offset=0, nsfw=True):
        get(
            "https://api.myanimelist.net/v2/anime",
            {
                "q": query,
                "nsfw": "true" if nsfw else "false",
                limit: limit,
                offset: offset,
            },
        )

    def get_anime_details(
        self,
        id: int,
        *,
        fields=[
            "synopsis",
            "start_date",
            "mean",
            "genres",
            "num_episodes",
            "rating",
            "studios",
            "pictures",
            "background",
            "alternative_titles",
        ],
        nsfw=True,
    ):
        pass
