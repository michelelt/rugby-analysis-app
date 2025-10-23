from typing import Optional

from PyQt6.QtCore import QTimer, QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QLabel, QSizePolicy, QVBoxLayout, QWidget


class VideoPlayerEmbed(QWidget):
    """
    Simple YouTube embed player using QWebEngineView.

    Usage:
        player = VideoPlayerEmbed()
        player.set_url("https://www.youtube.com/watch?v=XXXX")
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._view = QWebEngineView(self)
        self._info = QLabel("", self)
        self._info.setWordWrap(True)
        # Ensure the embed view expands to fill the available space
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._view.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        layout = QVBoxLayout(self)
        layout.addWidget(self._view, 1)
        layout.addWidget(self._info, 0)

    def _to_embed_url(self, url: str) -> str:
        """
        Convert common YouTube URLs to an embed URL.
        Examples handled:
            - https://www.youtube.com/watch?v=VIDEO_ID -> https://www.youtube.com/embed/VIDEO_ID
            - https://youtu.be/VIDEO_ID -> https://www.youtube.com/embed/VIDEO_ID
        If the URL already looks like an embed URL, it is returned unchanged.
        """
        if "youtube.com/embed/" in url:
            return url
        if "watch?v=" in url:
            return url.replace("watch?v=", "embed/")
        if "youtu.be/" in url:
            # short link -> embed
            parts = url.split("youtu.be/")
            if len(parts) > 1:
                video_id = parts[1].split("?")[0]
                return f"https://www.youtube.com/embed/{video_id}"
        return url

    def set_url(self, url: str, start_ms: int = 0) -> None:
        """
        Set the video URL. Automatically converts to embed URL where applicable.

        An optional start time (milliseconds) can be provided — the embed URL will
        receive the `start` parameter in seconds.
        """
        try:
            # remember the original provided URL (useful for persisting or reusing)
            self._orig_url = url.strip()
            embed = self._to_embed_url(self._orig_url)
            # store base for later seeks
            self._last_base = embed.split("?")[0]
            if start_ms and start_ms > 0:
                start_s = int(start_ms // 1000)
                url_with_start = f"{self._last_base}?start={start_s}"
                # remember last seek in seconds for play()
                self._last_seek_s = start_s
            else:
                url_with_start = self._last_base
                self._last_seek_s = 0
            self._view.setUrl(QUrl(url_with_start))
            self._info.setText("")
        except Exception as exc:  # keep robust and simple
            self._info.setText(f"Errore caricamento video: {exc}")

    def set_url_with_start(self, url: str, start_ms: int = 0) -> None:
        """Set the video URL and jump to start_ms (milliseconds).

        For embedded YouTube this adds the `start` parameter (in seconds).
        """
        # Keep backward compatibility but delegate to the normalized set_url
        self.set_url(url, start_ms=start_ms)

    def seek(self, ms: int) -> None:
        """Seek to ms milliseconds by reloading embed URL with start parameter."""
        if not hasattr(self, "_last_base"):
            # nothing loaded yet; show a short status so the user knows why
            try:
                self._info.setText("Nessun video caricato per il seek")
                QTimer.singleShot(3000, lambda: self._info.setText(""))
            except Exception:
                pass
            return
        try:
            start_s = int(max(0, ms // 1000))
            url_with_start = f"{self._last_base}?start={start_s}"
            # remember last seek in seconds so play() can enable autoplay
            self._last_seek_s = start_s
            self._view.setUrl(QUrl(url_with_start))
        except Exception as exc:
            # show a transient message so users aren't left guessing
            try:
                self._info.setText(f"Errore seek: {exc}")
                QTimer.singleShot(3000, lambda: self._info.setText(""))
            except Exception:
                pass

    def play(self) -> None:
        """Attempt to start playback for the embedded player.

        For YouTube embeds we try to reload the iframe with autoplay=1. Note that
        browser/autoplay policies may block audio autoplay; this will still try.
        """
        if not hasattr(self, "_last_base"):
            return
        try:
            # Build URL including start and autoplay
            params = []
            if hasattr(self, "_last_seek_s") and self._last_seek_s:
                params.append(f"start={int(self._last_seek_s)}")
            params.append("autoplay=1")
            sep = "?" if "?" not in self._last_base else "&"
            url = f"{self._last_base}{sep}{'&'.join(params)}"
            self._view.setUrl(QUrl(url))
        except Exception:
            # best-effort; ignore errors
            pass

    def clear(self) -> None:
        """Clear the player view."""
        self._view.setHtml("")
        self._info.setText("")

    def get_current_url(self) -> str:
        """Return the last-provided original URL for this player (or empty string)."""
        return getattr(self, "_orig_url", "")
