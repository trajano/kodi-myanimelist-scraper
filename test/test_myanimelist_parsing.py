from metadata_myanimelist_tv._myanimelist import (
    MyAnimeListAnime,
    MyAnimeListAlternativeTitles,
    MyAnimeListPicture,
)
from datetime import date


def test_parse_alternative_titles():
    shokugeki_alternative_titles = """
{
    "synonyms": [
      "Shokugeki no Soma",
      "Food Wars: Shokugeki no Soma"
    ],
    "en": "Food Wars! Shokugeki no Soma",
    "ja": "食戟のソーマ"
  }
"""
    alternative_titles = MyAnimeListAlternativeTitles.from_json(
        shokugeki_alternative_titles
    )
    assert "Shokugeki no Soma" in alternative_titles.all_titles()
    assert "Food Wars: Shokugeki no Soma" in alternative_titles.all_titles()
    assert "Food Wars! Shokugeki no Soma" in alternative_titles.all_titles()
    assert "食戟のソーマ" in alternative_titles.all_titles()


def test_parse_picture():
    picture = """{
    "medium": "https://cdn.myanimelist.net/images/anime/1444/148976.webp",
    "large": "https://cdn.myanimelist.net/images/anime/1444/148976l.webp"
  }"""
    MyAnimeListPicture.from_json(picture)


def test_parse_shokugeki():
    shokugeki = """
{
  "id": 28171,
  "title": "Shokugeki no Souma",
  "main_picture": {
    "medium": "https://cdn.myanimelist.net/images/anime/1444/148976.webp",
    "large": "https://cdn.myanimelist.net/images/anime/1444/148976l.webp"
  },
  "synopsis": "Souma Yukihira has been cooking alongside his father Jouichirou for as long as he can remember. As a sous chef at his father's restaurant, he has spent years developing his culinary expertise and inventing new dishes to amaze their customers. He aspires to exceed his father's skill and take over the restaurant one day, but he is shocked to learn that Jouichirou is closing up the shop to take a job in New York.\\n\\nRather than tagging along with his father, Souma finds himself enrolling at the prestigious Tootsuki Culinary Academy, where only 10 percent of its students end up graduating. The school is famous for its \\"Shokugeki\\"—intense cooking competitions between students often used to settle debates and arguments. Jouichirou tells Souma that to surpass him and survive the next three years at Tootsuki and graduate there.\\n\\nThe academy's brutal curriculum and fiercely competitive student body await the young chef, who must learn to navigate the treacherous environment if he wants to stand a chance at realizing his dreams. But is skill alone enough to let him rise to the top?\\n\\n[Written by MAL Rewrite]",
  "start_date": "2015-04-04",
  "mean": 8.12,
  "genres": [
    {
      "id": 9,
      "name": "Ecchi"
    },
    {
      "id": 47,
      "name": "Gourmet"
    },
    {
      "id": 23,
      "name": "School"
    },
    {
      "id": 27,
      "name": "Shounen"
    }
  ],
  "num_episodes": 24,
  "rating": "pg_13",
  "studios": [
    {
      "id": 7,
      "name": "J.C.Staff"
    }
  ],
  "pictures": [
    {
      "medium": "https://cdn.myanimelist.net/images/anime/11/68293.jpg",
      "large": "https://cdn.myanimelist.net/images/anime/11/68293l.jpg"
    },
    {
      "medium": "https://cdn.myanimelist.net/images/anime/4/75713.jpg",
      "large": "https://cdn.myanimelist.net/images/anime/4/75713l.jpg"
    },
    {
      "medium": "https://cdn.myanimelist.net/images/anime/5/76426.jpg",
      "large": "https://cdn.myanimelist.net/images/anime/5/76426l.jpg"
    },
    {
      "medium": "https://cdn.myanimelist.net/images/anime/13/76427.jpg",
      "large": "https://cdn.myanimelist.net/images/anime/13/76427l.jpg"
    },
    {
      "medium": "https://cdn.myanimelist.net/images/anime/1444/148976.jpg",
      "large": "https://cdn.myanimelist.net/images/anime/1444/148976l.jpg"
    },
    {
      "medium": "https://cdn.myanimelist.net/images/anime/1539/148977.jpg",
      "large": "https://cdn.myanimelist.net/images/anime/1539/148977l.jpg"
    }
  ],
  "background": "Shokugeki no Souma was released on Blu-ray and DVD as Food Wars! Shokugeki no Souma by Sentai Filmworks on August 15, 2017.",
  "alternative_titles": {
    "synonyms": [
      "Shokugeki no Soma",
      "Food Wars: Shokugeki no Soma"
    ],
    "en": "Food Wars! Shokugeki no Soma",
    "ja": "食戟のソーマ"
  }
}
"""
    anime = MyAnimeListAnime.from_json(shokugeki)
    assert "Shokugeki no Souma" in anime.all_titles()
    assert "Shokugeki no Soma" in anime.all_titles()
    assert "Food Wars: Shokugeki no Soma" in anime.all_titles()
    assert "Food Wars! Shokugeki no Soma" in anime.all_titles()
    assert "食戟のソーマ" in anime.all_titles()

    assert isinstance(anime.start_date, date)
