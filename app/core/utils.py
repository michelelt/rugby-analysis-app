import re

YT_REGEX = re.compile(
    r"^(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([A-Za-z0-9_-]{11})(?:[&?#].*)?$",
    re.IGNORECASE,
)


def is_valid_youtube_url(url: str) -> bool:
    """Quick heuristic validator for YouTube video URLs.

    Accepts full `youtube.com/watch?v=...` and short `youtu.be/...` forms.
    This is intentionally lightweight (no network calls).
    """
    if not url or not isinstance(url, str):
        return False
    url = url.strip()
    return bool(YT_REGEX.match(url))


def parse_minuto_to_ms(text: str) -> int:
    """Parse a minuto field to milliseconds.

    Accepts:
      - integer minutes: '3' -> 180000 ms
      - minute:second '1:23' -> 83000 ms
      - trakt variations ("1.23") will be attempted, fallback to int minutes

    Returns 0 on parse errors.
    """
    try:
        if not text:
            return 0
        text = str(text).strip()
        if ":" in text:
            parts = text.split(":")
            if len(parts) == 2:
                minutes = int(parts[0]) if parts[0] else 0
                seconds = int(parts[1]) if parts[1] else 0
                return (minutes * 60 + seconds) * 1000
        if "." in text:
            parts = text.split(".")
            if len(parts) == 2:
                minutes = int(parts[0]) if parts[0] else 0
                seconds = int(parts[1]) if parts[1] else 0
                return (minutes * 60 + seconds) * 1000
        # plain integer or float representing minutes
        minutes = int(float(text))
        return minutes * 60 * 1000
    except Exception:
        return 0
