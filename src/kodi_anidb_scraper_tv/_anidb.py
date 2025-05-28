import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import date
from ._util import remove_anidb_markup

from typing import Optional, List
import requests

# This is better used as Genre
ELEMENTS_TAG_ID = 2611

# This is better used to get the MPAA rating
TARGET_AUDIENCE_TAG_ID = 2606

# Mapping of target audience child tags to MPAA ratings
TARGET_AUDIENCE_TAG_ID_TO_MPAA = {
    2615: "NC-17",  # 18 restricted
    2614: "R",  # josei
    1802: "R",  # seinen
    2616: "G",  # mina
    1846: "G",  # kodomo
    922: "PG-13",  # shounen
    1077: "PG-13",  # shoujo
}


@dataclass
class AniDbTag:
    id: int
    parentid: Optional[int]
    weight: float
    localspoiler: bool
    globalspoiler: bool
    verified: bool
    update: Optional[date]
    name: str
    description: Optional[str]
    picurl: Optional[str]

    def __init__(self, el: ET.Element):
        self.name = remove_anidb_markup(el.findtext("name"))
        self.id = int(el.attrib["id"])
        self.parentid = int(pid) if (pid := el.get("parentid")) else None
        self.weight = int(el.attrib["weight"])
        self.globalspoiler = el.attrib["globalspoiler"] == "true"
        self.localspoiler = el.attrib["localspoiler"] == "true"
        self.verified = el.attrib["verified"] == "true"
        self.description = (
            remove_anidb_markup(el.findtext("description"))
            if el.findtext("description")
            else None
        )
        self.picurl = el.findtext("picurl")
        self.update = (
            date.fromisoformat(update_date)
            if (update_date := el.findtext("update"))
            else None
        )

        # <character id="71248" type="main character in" update="2020-09-18">
        #     <rating votes="200">8.78</rating>
        #     <name>Yukihira Souma</name>
        #     <gender>male</gender>
        #     <charactertype id="1">Character</charactertype>
        #     <picture>163937.jpg</picture>
        #     <seiyuu id="20249" picture="186289.jpg">Matsuoka Yoshitsugu</seiyuu>
        # </character>


@dataclass
class AniDbRating:
    votes: int
    mean: float

    def __init__(self, el: ET.Element):
        self.votes = int(el.attrib["votes"])
        self.mean = float(el.text or 0)


# #     <ratings>
#         <permanent count="5020">7.89</permanent>
#         <temporary count="5053">7.85</temporary>
#         <review count="2">7.75</review>
#     </ratings>


@dataclass
class AniDbRatingsRating:
    """Anime level ratings rating. This is not built using the element."""

    count: int
    mean: float


@dataclass
class AniDbRatings:
    permanent: AniDbRatingsRating
    temporary: AniDbRatingsRating
    review: AniDbRatingsRating

    def __init__(self, el: ET.Element):
        permanent_element = el.find("permanent")
        temporary_element = el.find("temporary")
        review_element = el.find("review")
        assert permanent_element is not None
        assert temporary_element is not None
        assert review_element is not None
        self.permanent = AniDbRatingsRating(
            count=int(permanent_element.attrib["count"]),
            mean=float(permanent_element.text or 0),
        )
        self.temporary = AniDbRatingsRating(
            count=int(temporary_element.attrib["count"]),
            mean=float(temporary_element.text or 0),
        )
        self.review_element = AniDbRatingsRating(
            count=int(review_element.attrib["count"]),
            mean=float(review_element.text or 0),
        )


@dataclass
class AniDbSeiyuu:
    id: int
    name: str
    picture: Optional[str]

    def __init__(self, el: ET.Element):
        self.id = int(el.attrib["id"])
        self.name = remove_anidb_markup(el.text)
        self.picture = el.attrib["picture"]


@dataclass
class AniDbCharacterType:
    id: int
    name: str

    def __init__(self, el: ET.Element):
        self.id = int(el.attrib["id"])
        self.name = remove_anidb_markup(el.text)


@dataclass
class AniDbCharacter:
    id: int
    type: str
    rating: Optional[AniDbRating]
    update: Optional[date]
    name: str
    gender: Optional[str]
    charactertype: Optional[AniDbCharacterType]
    seiyuu: Optional[AniDbSeiyuu]
    picture: Optional[str]

    def __init__(self, el: ET.Element):
        self.id = int(el.attrib["id"])
        self.type = el.attrib["type"]
        self.name = remove_anidb_markup(el.findtext("name"))
        self.gender = el.findtext("gender")
        self.charactertype = (
            AniDbCharacterType(elem) if (elem := el.find("charactertype")) else None
        )
        self.rating = AniDbRating(elem) if (elem := el.find("rating")) else None
        self.seiyuu = AniDbSeiyuu(elem) if (elem := el.find("seiyuu")) else None
        self.picture = el.findtext("picture")
        self.update = (
            date.fromisoformat(update_date)
            if (update_date := el.findtext("update"))
            else None
        )


@dataclass
class AniDbTitle:
    lang: str
    text: str
    title_type: Optional[str] = None

    def __init__(self, el: ET.Element):
        self.text = remove_anidb_markup(el.text)
        self.lang = el.attrib["{http://www.w3.org/XML/1998/namespace}lang"]
        self.title_type = el.attrib["type"]

    @property
    def is_official(self):
        return self.title_type == "official"

    @property
    def is_main(self):
        return self.title_type == "main"

    @property
    def is_synonym(self):
        return self.title_type == "syn"

    @property
    def lower(self) -> str:
        return self.text.lower()


@dataclass
class AniDbAnime:
    id: int
    restricted: bool
    type: str
    titles: List[AniDbTitle]
    tags: List[AniDbTag]
    characters: List[AniDbCharacter]
    ratings: AniDbRatings
    el: ET.Element
    start_date: Optional[date] = None
    end_date: Optional[date] = None

    def __init__(self, el: ET.Element):
        self.id = int(el.attrib["id"])
        self.restricted = el.attrib["restricted"] == "true"
        self.type = el.findtext("type", default="")
        self.titles = []
        titles_element = el.find("titles")
        assert titles_element
        for title_element in titles_element.iter("title"):
            self.titles.append(AniDbTitle(title_element))

        self.tags = []
        tags_element = el.find("tags")
        assert tags_element
        for tag_element in tags_element.iter("tag"):
            self.tags.append(AniDbTag(tag_element))

        self.characters = []
        characters_element = el.find("characters")
        assert characters_element
        for character_element in characters_element.iter("character"):
            self.characters.append(AniDbCharacter(character_element))

        ratings_element = el.find("ratings")
        assert ratings_element
        self.ratings = AniDbRatings(ratings_element)

        start_date = el.findtext("startdate")
        if start_date:
            self.start_date = date.fromisoformat(start_date)

        end_date = el.findtext("enddate")
        if end_date:
            self.end_date = date.fromisoformat(end_date)
        self.el = el

    def official_title(self, lang: str) -> str:
        # try official in requested lang, then Japanese, then English
        for lang_checked in (lang, "ja", "en"):
            title = next(
                (
                    t.text
                    for t in self.titles
                    if t.is_official and t.lang == lang_checked
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

    @property
    def description(self) -> str:
        return remove_anidb_markup(self.el.findtext("description"))

    @property
    def tag_names(self) -> List[str]:
        return [
            tag.name
            for tag in self.tags
            if tag.parentid != ELEMENTS_TAG_ID
            and tag.parentid != TARGET_AUDIENCE_TAG_ID
        ]

    @property
    def genres(self) -> List[str]:
        return [tag.name for tag in self.tags if tag.parentid == ELEMENTS_TAG_ID]

    @property
    def mpaa_rating(self) -> Optional[str]:
        """Look for a target‐audience tag and map it to MPAA."""
        for tag in self.tags:
            if tag.parentid == TARGET_AUDIENCE_TAG_ID:
                return TARGET_AUDIENCE_TAG_ID_TO_MPAA.get(tag.id)
        return None  # no matching audience tag found


class AniDb:
    def __init__(
        self, client_id: str, client_version: int, anidb_proxy: Optional[str] = None
    ):
        self.client_id = client_id
        self.client_version = client_version
        self.anidb_base_url = anidb_proxy or "http://api.anidb.net:9001"

    def get(self, aid: int) -> AniDbAnime:
        url = f"{self.anidb_base_url}/httpapi?request=anime&aid={aid}&client={self.client_id}&clientver={self.client_version}&protover=1"
        response = requests.get(url)
        response.raise_for_status()
        return AniDbAnime(ET.fromstring(response.text))
