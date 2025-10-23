import pytest


@pytest.mark.skipif(True, reason="Requires GUI environment; run manually")
def test_embed_player_smoke():
    # This test is a placeholder: run manually in a GUI-enabled env
    import sys

    from PyQt6.QtWidgets import QApplication

    from app.ui.video_player_embed import VideoPlayerEmbed

    app = QApplication.instance() or QApplication(sys.argv)
    w = VideoPlayerEmbed(None)
    # basic contract: methods exist
    assert hasattr(w, "set_url")
    assert hasattr(w, "seek")
    assert hasattr(w, "play")


@pytest.mark.skipif(True, reason="Requires GUI + media libs; run manually")
def test_stream_player_smoke():
    import sys

    from PyQt6.QtWidgets import QApplication

    from app.ui.video_player_stream import VideoPlayerStream

    app = QApplication.instance() or QApplication(sys.argv)
    w = VideoPlayerStream(None)
    assert hasattr(w, "set_url")
    assert hasattr(w, "seek")
    assert hasattr(w, "play")
