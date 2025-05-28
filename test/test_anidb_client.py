import pytest
from kodi_anidb_scraper_tv._anidb import AniDb
from kodi_anidb_scraper_tv._animetitles import load_anime_titles, AnimeTitles
from dotenv import load_dotenv
import os
import xml.etree.ElementTree as ET

# load .env at test runtime
load_dotenv()


@pytest.fixture
def anidb_client():
    client_id = os.getenv("ANIDB_CLIENT_ID")
    client_version = int(os.getenv("ANIDB_CLIENT_VERSION", "0"))
    if client_id is None:
        pytest.skip("ANIDB_CLIENT_ID not set in .env, skipping live API tests")
    return AniDb(client_id=client_id, client_version=client_version)


def test_client(anidb_client: AniDb):
    anime = anidb_client.get(10901)
    assert anime is not None


def test_fetch_files():
    with load_anime_titles("anime-files.xml.gz") as loaded:
        parsed = ET.parse(loaded)
        titles = AnimeTitles(parsed.getroot())
        count = sum(1 for _ in parsed.iter("anime"))
        assert count == len(titles.animes)


def test_search():
    with load_anime_titles("anime-files.xml.gz") as loaded:
        parsed = ET.parse(loaded)
        titles = AnimeTitles(parsed.getroot())
        assert len(titles.find_all_by_title("food Wars!")) > 0
