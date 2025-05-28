from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse, parse_qs


@dataclass
class AniDbUrl:
    aid: int
    episode_num: Optional[str] = None
    episode_count_hint: Optional[int] = None

    @property
    def url(self) -> str:
        if self.episode_num is None and self.episode_count_hint is None:
            return f"anidb:/animes/{self.aid}"
        elif self.episode_num is not None and self.episode_count_hint is None:
            return f"anidb:/animes/{self.aid}/episodes/{self.episode_num}"
        elif self.episode_num is None and self.episode_count_hint is not None:
            return f"anidb:/animes/{self.aid}?episode_count={self.episode_count_hint}"
        else:
            return (
                f"anidb:/animes/{self.aid}"
                f"/episodes/{self.episode_num}"
                f"?episode_count={self.episode_count_hint}"
            )

    @property
    def episode_guide_url(self) -> str:
        if self.episode_count_hint is None:
            return f"anidb:/animes/{self.aid}/episodes"
        else:
            return f"anidb:/animes/{self.aid}/episodes?episode_count={self.episode_count_hint}"

    @classmethod
    def from_url(cls, url: str) -> "AniDbUrl":
        parsed = urlparse(url)
        # path parts: ['', 'animes', '{aid}', 'episodes', '{episode_num}']
        parts = parsed.path.lstrip("/").split("/")
        aid = int(parts[1]) if len(parts) > 1 and parts[0] == "animes" else None
        assert aid
        episode_num = None
        if len(parts) >= 4 and parts[2] == "episodes":
            episode_num = parts[3]
        qs = parse_qs(parsed.query)
        hint_vals = qs.get("episode_count")
        episode_count_hint = int(hint_vals[0]) if hint_vals else None
        return cls(
            aid=aid, episode_num=episode_num, episode_count_hint=episode_count_hint
        )
