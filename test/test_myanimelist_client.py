import pytest
from metadata_myanimelist_tv._myanimelist import MyAnimeList
from metadata_myanimelist_tv._anime_news_network import AnimeNewsNetworkEncyclopedia
from dotenv import load_dotenv
import os

# load .env at test runtime
load_dotenv()


@pytest.fixture
def mal_client():
    client_id = os.getenv("MAL_CLIENT_ID")
    if client_id is None:
        pytest.skip("MAL_CLIENT_ID not set in .env, skipping live API tests")
    return MyAnimeList(client_id=client_id)


def test_client(mal_client: MyAnimeList):
    # check .env file for MAL_CLIENT_ID if not skip test
    query_result = mal_client.find_anime("Shokugeki no Soma")
    assert query_result is not None
    anime_id = query_result.data[0].node.id
    anime = mal_client.get_anime_details(anime_id)
    assert anime.mpaa_rating == "PG-13"
    assert anime.airing_status == "Finished"


def test_with_ann(mal_client: MyAnimeList):
    # check .env file for MAL_CLIENT_ID if not skip test
    query_result = mal_client.find_anime("Shokugeki no Soma")
    assert query_result is not None
    anime_id = query_result.data[0].node.id
    anime = mal_client.get_anime_details(anime_id)
    assert anime.mpaa_rating == "PG-13"
    assert anime.airing_status == "Finished"
    ann = AnimeNewsNetworkEncyclopedia()
    ann_entry = ann.get_anime(anime.all_titles)
    print(ann_entry)
