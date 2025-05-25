from dataclasses import dataclass
from requests import get


@dataclass
class MyAnimeListMainPicture:
    medium: str
    large: str | None

    def url(self) -> str:
        return self.large or self.medium


@dataclass
class MyAnimeListAnime:
    id: int
    title: str
    main_pictuture: MyAnimeListMainPicture


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
