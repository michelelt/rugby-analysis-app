from controllers.evento_controller import EventoController
from PyQt6 import QtCore
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)


class MatchSelector(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select or Create Match")
        self.controller = EventoController()
        self.selected_match_id = None

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Select an existing match or create a new one:"))

        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        btn_layout = QHBoxLayout()
        self.open_btn = QPushButton("Open")
        self.open_btn.clicked.connect(self.open_match)
        btn_layout.addWidget(self.open_btn)

        self.create_btn = QPushButton("Create New")
        self.create_btn.clicked.connect(self.create_match)
        btn_layout.addWidget(self.create_btn)

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.load_matches)
        btn_layout.addWidget(self.refresh_btn)

        self.delete_btn = QPushButton("Delete")
        self.delete_btn.clicked.connect(self.delete_match)
        btn_layout.addWidget(self.delete_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

        self.load_matches()

    def load_matches(self):
        self.list_widget.clear()
        rows = self.controller.lista_matches()
        for r in rows:
            # r = (id, name, data, squadra_home, squadra_away)
            display = f"{r[1] or 'Match ' + str(r[0])} - {r[2]} {r[3]} vs {r[4]}"
            item = QListWidgetItem(display)
            # use ItemDataRole enum for user role
            try:
                role = QtCore.Qt.ItemDataRole.UserRole
            except Exception:
                # fallback numeric
                role = 32
            item.setData(role, r[0])
            self.list_widget.addItem(item)

    def open_match(self):
        item = self.list_widget.currentItem()
        if not item:
            QMessageBox.information(self, "Select", "Please select a match first")
            return
        try:
            try:
                role = QtCore.Qt.ItemDataRole.UserRole
            except Exception:
                role = 32
            match_id = item.data(role)
        except Exception:
            match_id = None
        self.selected_match_id = match_id
        self.accept()

    def delete_match(self):
        item = self.list_widget.currentItem()
        if not item:
            QMessageBox.information(self, "Select", "Please select a match first")
            return
        try:
            try:
                role = QtCore.Qt.ItemDataRole.UserRole
            except Exception:
                role = 32
            match_id = item.data(role)
        except Exception:
            match_id = None
        if not match_id:
            QMessageBox.warning(self, "Error", "Unable to determine match id")
            return
        confirm = QMessageBox.question(
            self,
            "Confirm",
            f"Delete match id={match_id}? This will unlink any events.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return
        try:
            self.controller.elimina_match(match_id)
            QMessageBox.information(self, "Deleted", f"Match id={match_id} deleted.")
            self.load_matches()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Unable to delete match: {e}")

    def create_match(self):
        # Simplified match creation: only ask for date and team names
        data, ok = QInputDialog.getText(self, "Date", "Date (dd/MM/yyyy):")
        if not ok:
            return
        squadra_home, ok = QInputDialog.getText(self, "Home Team", "Squadra Home:")
        if not ok:
            return
        squadra_away, ok = QInputDialog.getText(self, "Away Team", "Squadra Away:")
        if not ok:
            return
        name = f"{squadra_home} vs {squadra_away} {data}"
        match = {
            "name": name,
            "data": data,
            "squadra_home": squadra_home,
            "squadra_away": squadra_away,
            "minuto_kickoff": "",
            "video_url": "",
        }
        match_id = self.controller.salva_match(match)
        QMessageBox.information(self, "Created", f"Match created id={match_id}")
        # return the created match so the caller can open it immediately
        self.selected_match_id = match_id
        self.accept()
