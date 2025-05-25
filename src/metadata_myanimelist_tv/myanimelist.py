from dataclasses import dataclass, field
from datetime import date
from dataclasses_json import dataclass_json, Undefined, CatchAll, config
from requests import get
from typing import List, Optional, Set
from marshmallow import fields


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

    def all_titles(self) -> Set[str]:
        return set(self.synonyms) | set(self.titles.values())


@dataclass_json
@dataclass
class MyAnimeListAnime:
    id: int
    title: str
    main_picture: MyAnimeListPicture
    synopsis: Optional[str]

    mean: Optional[float]
    genres: Optional[List[MyAnimeListGenre]]
    num_episodes: Optional[int]
    rating: Optional[str]
    studios: Optional[List[MyAnimeListStudio]]
    pictures: Optional[List[MyAnimeListPicture]]
    background: Optional[str]
    alternative_titles: Optional[MyAnimeListAlternativeTitles]

    start_date: Optional[date] = field(
        default=None,
        metadata=config(
            encoder=date.isoformat, decoder=date.fromisoformat, mm_field=fields.Date()
        ),
    )
    end_date: Optional[date] = field(
        default=None,
        metadata=config(
            encoder=date.isoformat, decoder=date.fromisoformat, mm_field=fields.Date()
        ),
    )

    def all_titles(self) -> Set[str]:
        # gather alt titles if present, then add the main title
        alt_set = (
            self.alternative_titles.all_titles() if self.alternative_titles else set()
        )
        return alt_set | {self.title}


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
