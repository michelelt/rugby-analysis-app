from typing import Optional

import yt_dlp
from PyQt6.QtCore import Qt, QTimer, QUrl
from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSlider,
    QVBoxLayout,
    QWidget,
)


class VideoPlayerStream(QWidget):
    """
    Stream player using QMediaPlayer + QVideoWidget.
    Uses yt_dlp to extract a direct streamable URL from YouTube.

    Controls: Play, Pause, Stop, Volume, Seek.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        # Media objects
        self._player = QMediaPlayer(self)
        self._audio = QAudioOutput(self)
        self._player.setAudioOutput(self._audio)
        self._video_widget = QVideoWidget(self)
        self._player.setVideoOutput(self._video_widget)

        # Info / error label
        self._info_label = QLabel("", self)
        self._info_label.setWordWrap(True)

        # Controls
        self._play_btn = QPushButton("Play", self)
        self._pause_btn = QPushButton("Pause", self)
        self._stop_btn = QPushButton("Stop", self)

        self._volume_slider = QSlider(Qt.Orientation.Horizontal, self)
        self._volume_slider.setRange(0, 100)
        self._volume_slider.setValue(50)
        self._audio.setVolume(0.5)

        self._position_slider = QSlider(Qt.Orientation.Horizontal, self)
        self._position_slider.setRange(0, 0)

        # Layout
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self._play_btn)
        btn_layout.addWidget(self._pause_btn)
        btn_layout.addWidget(self._stop_btn)
        btn_layout.addWidget(QLabel("Vol:", self))
        btn_layout.addWidget(self._volume_slider)

        main_layout = QVBoxLayout(self)
        # Make the video widget expand and take most space
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._video_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        main_layout.addWidget(self._video_widget, 1)
        main_layout.addLayout(btn_layout)
        main_layout.addWidget(self._position_slider)
        # Time label shows current position / duration (e.g. 00:01 / 01:23:45)
        self._time_label = QLabel("00:00 / 00:00", self)
        self._time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self._time_label)
        main_layout.addWidget(self._info_label)

        # Connections
        self._play_btn.clicked.connect(self._player.play)
        self._pause_btn.clicked.connect(self._player.pause)
        self._stop_btn.clicked.connect(self._player.stop)
        self._volume_slider.valueChanged.connect(self._on_volume_changed)
        self._position_slider.sliderMoved.connect(self._on_seek)

        self._player.positionChanged.connect(self._on_position_changed)
        self._player.durationChanged.connect(self._on_duration_changed)
        self._player.errorOccurred.connect(self._on_error)

    def _on_volume_changed(self, value: int) -> None:
        self._audio.setVolume(max(0.0, min(1.0, value / 100.0)))

    def _on_seek(self, position: int) -> None:
        self._player.setPosition(position)

    def _on_position_changed(self, pos: int) -> None:
        # QMediaPlayer emits a 64-bit position; ensure we use an int for the slider
        try:
            p = int(pos)
        except Exception:
            p = 0
        self._position_slider.blockSignals(True)
        self._position_slider.setValue(p)
        self._position_slider.blockSignals(False)
        # Update time label (position / duration)
        try:
            duration = (
                int(self._player.duration())
                if self._player.duration() is not None
                else 0
            )
        except Exception:
            duration = 0
        self._time_label.setText(
            f"{self._format_time(p)} / {self._format_time(duration)}"
        )

    def _on_duration_changed(self, duration: int) -> None:
        try:
            d = int(duration)
        except Exception:
            d = 0
        self._position_slider.setRange(0, d)
        # Update time label to show new duration (current position may be zero)
        try:
            pos = (
                int(self._player.position())
                if self._player.position() is not None
                else 0
            )
        except Exception:
            pos = 0
        self._time_label.setText(f"{self._format_time(pos)} / {self._format_time(d)}")

    def _format_time(self, ms: int) -> str:
        """Format milliseconds to H:MM:SS or M:SS if hours == 0."""
        try:
            total_seconds = max(0, int(ms) // 1000)
        except Exception:
            total_seconds = 0
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        if hours:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        return f"{minutes}:{seconds:02d}"

    def _on_error(self, error):
        # Display a readable message; keep simple
        self._info_label.setText(f"Player error: {self._player.errorString()}")

    def _select_stream_url(self, info: dict) -> Optional[str]:
        """
        Choose a suitable stream URL from yt_dlp info dict.
        Prefer a direct http(s) url from formats or info['url'] when present.
        """
        if not info:
            return None
        if "url" in info and isinstance(info["url"], str):
            return info["url"]
        formats = info.get("formats") or []
        # Try to prefer a format that has 'protocol' http/https and has a url
        for fmt in reversed(formats):  # reversed often yields higher quality later
            url = fmt.get("url")
            protocol = fmt.get("protocol", "")
            if url and protocol.startswith("http"):
                return url
        # Fallback to first available format url
        for fmt in formats:
            if fmt.get("url"):
                return fmt.get("url")
        return None

    def set_url(self, url: str, start_ms: int = 0) -> None:
        """
        Extract a direct stream URL from YouTube via yt_dlp and set it on the player.
        If extraction fails, show an error message.
        """
        # remember the original URL provided by the user
        self._orig_url = url.strip()
        self._info_label.setText("Caricamento video...")
        try:
            ydl_opts = {
                "quiet": True,
                "skip_download": True,
                "no_warnings": True,
                "format": "best",
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url.strip(), download=False)
            info_dict = info if isinstance(info, dict) else {}
            stream_url = self._select_stream_url(info_dict)
            if not stream_url:
                raise RuntimeError("Nessun flusso disponibile dal link fornito.")
            # Use QUrl to set media source
            self._player.setSource(QUrl(stream_url))
            self._info_label.setText("")
            # Auto-play after setting source
            self._player.play()
            # If a start_ms was requested, schedule a seek after play begins
            if start_ms and start_ms > 0:
                try:
                    # Some backends require a short delay; setPosition should work after source set
                    self._player.setPosition(int(start_ms))
                except Exception:
                    pass
        except Exception as exc:
            self._info_label.setText(f"Errore estrazione/streaming: {exc}")

    def clear(self) -> None:
        """Stop and clear the current media."""
        try:
            self._player.stop()
            self._player.setSource(QUrl())
            self._info_label.setText("")
        except Exception:
            pass

    def seek(self, ms: int) -> None:
        """Seek to the given position in milliseconds."""
        try:
            # If no source is set, inform the user briefly
            if not self._player.source() or not str(self._player.source().toString()):
                try:
                    self._info_label.setText("Nessun media caricato per il seek")
                    QTimer.singleShot(3000, lambda: self._info_label.setText(""))
                except Exception:
                    pass
                return
            self._player.setPosition(int(ms))
        except Exception as exc:
            try:
                self._info_label.setText(f"Errore seek: {exc}")
                QTimer.singleShot(3000, lambda: self._info_label.setText(""))
            except Exception:
                pass

    def play(self) -> None:
        """Start playback using the underlying QMediaPlayer."""
        try:
            self._player.play()
        except Exception:
            pass

    def get_current_url(self) -> str:
        """Return the last-provided original URL for this player (or empty string)."""
        return getattr(self, "_orig_url", "")
