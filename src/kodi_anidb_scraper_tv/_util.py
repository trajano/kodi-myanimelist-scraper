import re
from typing import Optional


def remove_anidb_markup(s: Optional[str]) -> str:
    if s is None:
        return ""
    # remove leading URL + space
    s = re.sub(r"\bhttps?://\S+\s+\[([^\]]+?)\]\B", r"\1", s)
    # replace grave‐accent with apostrophe
    return s.replace("`", "'")
