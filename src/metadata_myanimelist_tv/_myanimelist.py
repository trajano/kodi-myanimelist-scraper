from dataclasses import dataclass, field
from datetime import date
from dataclasses_json import (
    dataclass_json,
    Undefined,
    CatchAll,
    config,
    DataClassJsonMixin,
)
from requests import get
from typing import List, Optional, Set
from marshmallow import fields


@dataclass_json
@dataclass
class MyAnimeListPicture(DataClassJsonMixin):
    medium: str
    large: Optional[str]

    @property
    def url(self) -> str:
        return self.large or self.medium


@dataclass_json
@dataclass
class MyAnimeListGenre(DataClassJsonMixin):
    id: int
    name: str


@dataclass_json
@dataclass
class MyAnimeListStudio(DataClassJsonMixin):
    id: int
    name: str


@dataclass_json(undefined=Undefined.INCLUDE)
@dataclass
class MyAnimeListAlternativeTitles(DataClassJsonMixin):
    synonyms: List[str]
    titles: CatchAll
    en: Optional[str] = None
    ja: Optional[str] = None

    @property
    def all_titles(self) -> Set[str]:
        result: Set[str] = set(self.synonyms)

        if isinstance(self.titles, dict):
            # add all values from the titles dict
            result |= set(self.titles.values())

        # add the optional en/ja if present
        if self.en:
            result.add(self.en)
        if self.ja:
            result.add(self.ja)

        return result


@dataclass_json
@dataclass
class MyAnimeListAnime(DataClassJsonMixin):
    id: int
    title: str
    main_picture: MyAnimeListPicture
    synopsis: Optional[str] = None

    mean: Optional[float] = 0.0
    genres: Optional[List[MyAnimeListGenre]] = None
    num_episodes: Optional[int] = 0
    num_scoring_users: Optional[int] = 0
    rating: Optional[str] = None
    status: Optional[str] = None
    studios: Optional[List[MyAnimeListStudio]] = None
    pictures: Optional[List[MyAnimeListPicture]] = None
    background: Optional[str] = ""
    alternative_titles: Optional[MyAnimeListAlternativeTitles] = None

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

    @property
    def all_titles(self) -> Set[str]:
        # gather alt titles if present, then add the main title
        alt_set = (
            self.alternative_titles.all_titles if self.alternative_titles else set()
        )
        return alt_set | {self.title}

    @property
    def original_title(self) -> str:
        if self.alternative_titles is not None:
            if self.alternative_titles.ja is not None:
                return self.alternative_titles.ja
            if self.alternative_titles.en is not None:
                return self.alternative_titles.en
        return self.title

    @property
    def en_title(self) -> str:
        if self.alternative_titles is not None:
            if self.alternative_titles.en is not None:
                return self.alternative_titles.en
        return self.title

    @property
    def mpaa_rating(self) -> Optional[str]:
        if self.rating == "g":
            return "G"
        if self.rating == "pg":
            return "PG"
        if self.rating == "pg_13":
            return "PG-13"
        if self.rating == "r":
            return "R"
        if self.rating == "r+":
            return "R"
        if self.rating == "rx":
            return "NC-17"
        return None

    @property
    def airing_status(self) -> Optional[str]:
        if self.status == "finished_airing":
            return "Finished"
        if self.status == "currently_airing":
            return "Airing"
        if self.status == "not_yet_aired":
            return "Not yet aired"
        return None


@dataclass_json
@dataclass
class MyAnimeListQueryResultNode(DataClassJsonMixin):
    node: MyAnimeListAnime


@dataclass_json
@dataclass
class MyAnimeListQueryPaging(DataClassJsonMixin):
    prev: Optional[str] = None
    next: Optional[str] = None


@dataclass_json
@dataclass
class MyAnimeListQueryResult(DataClassJsonMixin):
    data: List[MyAnimeListQueryResultNode]
    paging: MyAnimeListQueryPaging


class MyAnimeList:
    def __init__(self, client_id: str) -> None:
        self.client_id = client_id

    def find_anime(
        self, query: str, *, limit=100, offset=0, nsfw=True
    ) -> MyAnimeListQueryResult:
        resp = get(
            "https://api.myanimelist.net/v2/anime",
            {
                "q": query,
                "nsfw": "true" if nsfw else "false",
                limit: limit,
                offset: offset,
            },
            headers={"X-MAL-CLIENT-ID": self.client_id},
        )
        return MyAnimeListQueryResult.from_json(resp.content)

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
            "num_scoring_users",
            "rating",
            "status",
            "studios",
            "pictures",
            "background",
            "alternative_titles",
        ],
        nsfw=True,
    ):
        resp = get(
            f"https://api.myanimelist.net/v2/anime/{id}",
            {"nsfw": "true" if nsfw else "false", "fields": ",".join(fields)},
            headers={"X-MAL-CLIENT-ID": self.client_id},
        )
        return MyAnimeListAnime.from_json(resp.content)
