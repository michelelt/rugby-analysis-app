import sys

from core.database import init_db
from PyQt6.QtWidgets import QApplication, QDialog
from ui.main_window import MainWindow
from ui.match_selector import MatchSelector


def main():
    init_db()
    app = QApplication(sys.argv)
    # Show a small match selector at startup
    selector = MatchSelector()
    selected_match = None
    # QDialog.exec() returns a DialogCode; compare against Accepted
    from PyQt6.QtWidgets import QDialog as _QDialog

    if selector.exec() == _QDialog.DialogCode.Accepted:
        selected_match = selector.selected_match_id

    window = MainWindow(match_id=selected_match)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
