from controllers.evento_controller import EventoController
from core.utils import is_valid_youtube_url, parse_minuto_to_ms
from PyQt6.QtCore import QDate, QPoint, Qt, QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMenu,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

# New imports for the two player options
from ui.video_player_embed import VideoPlayerEmbed
from ui.video_player_stream import VideoPlayerStream


class MainWindow(QWidget):
    """
    Main application window. The boolean flag `use_embed` (below) controls which
    video player implementation is instantiated and displayed below the events table.
    """

    use_embed = True  # set to False to use the stream player (QMediaPlayer + yt_dlp)

    def __init__(self, match_id=None):
        super().__init__()
        self.setWindowTitle("Analisi Rugby")
        self.setGeometry(100, 100, 1500, 700)
        self.controller = EventoController()
        self.match_id = match_id
        # -1 means "not editing"; use integer index for rows when editing
        self.editing_row = -1
        # When editing an existing evento we store its DB id here. None means not editing.
        self.editing_evento_id = None

        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        # --- Lato sinistro: form ---
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_widget.setLayout(left_layout)
        main_layout.addWidget(left_widget, 3)

        self.init_form(left_layout)
        # transient status label for validation/messages
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #d9534f;")
        left_layout.addWidget(self.status_label)
        self.save_button = QPushButton("Salva Evento")
        self.save_button.clicked.connect(self.salva_evento)
        left_layout.addWidget(self.save_button)

        # Button to save or link current session as a Match
        self.save_match_btn = QPushButton("Save Match")
        self.save_match_btn.setToolTip(
            "Save current session as a Match and link events"
        )
        self.save_match_btn.clicked.connect(self.save_match)
        left_layout.addWidget(self.save_match_btn)

        # Button to change/select a different match
        self.change_match_btn = QPushButton("Change Match")
        self.change_match_btn.setToolTip("Select or create a different match")
        self.change_match_btn.clicked.connect(self.change_match)
        left_layout.addWidget(self.change_match_btn)

        # --- Lato destro: tabella ---
        self.table = QTableWidget()
        # include 'Giocatore' and one column for Video URL (before ID)
        self.table.setColumnCount(18)
        self.table.setHorizontalHeaderLabels(
            [
                "Data",
                "Squadra Home",
                "Squadra Away",
                "Giocatore",
                "Minuto Kickoff",
                "Minuto",
                "Tipo fase",
                "Evento principale",
                "Origine possesso",
                "Num fasi",
                "Zona",
                "Esito",
                "Linea guadagno",
                "Velocità ruck",
                "Penalità",
                "Commento",
                "Video URL",
                "ID",
            ]
        )
        hh = self.table.horizontalHeader()
        if hh is not None:
            hh.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.menu_contenstuale)
        # Ensure table expands vertically to share space with the video container
        self.table.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        # When a table row is clicked, load the video at the 'Minuto' column time
        self.table.cellClicked.connect(self.on_table_cell_clicked)
        # --- Lato destro: tabella + video ---
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_widget.setLayout(right_layout)
        main_layout.addWidget(right_widget, 5)

        # --- Video mode selector (placed above the table) ---
        mode_bar = QWidget()
        mode_layout = QHBoxLayout(mode_bar)
        mode_layout.setContentsMargins(0, 0, 0, 0)
        mode_label = QLabel("Video Mode:")
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Embed (YouTube iframe)", "Stream (Direct link)"])
        # remember current mode
        self.current_video_mode = "embed" if self.use_embed else "stream"
        self.mode_combo.setCurrentIndex(0 if self.use_embed else 1)
        # connect change -> switch player
        self.mode_combo.currentIndexChanged.connect(
            lambda idx: self.switch_video_player("embed" if idx == 0 else "stream")
        )
        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(self.mode_combo)
        # Button to add/set the currently loaded video URL
        self.add_video_btn = QPushButton("Add Video")
        self.add_video_btn.setToolTip("Add or change the current video URL")
        self.add_video_btn.clicked.connect(self.add_video)
        mode_layout.addWidget(self.add_video_btn)
        # Keep mode bar compact vertically
        mode_bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        right_layout.addWidget(mode_bar)

        # Create a vertical splitter so the table and video are resizable by the user
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Table (top pane)
        self.table.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        splitter.addWidget(self.table)

        # Video container (bottom pane)
        self.video_container = QWidget()
        self.video_container_layout = QVBoxLayout(self.video_container)
        self.video_container_layout.setContentsMargins(0, 0, 0, 0)

        # instantiate initial player according to use_embed
        if self.use_embed:
            self.video_player = VideoPlayerEmbed(self)
        else:
            self.video_player = VideoPlayerStream(self)
        # ensure the player expands to fill the container
        self.video_player.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.video_container_layout.addWidget(self.video_player)

        self.video_container.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        splitter.addWidget(self.video_container)

        # Set initial splitter sizes so the video occupies ~2/3 of vertical space
        # We'll set a 1:2 ratio (table:video). Sizes are arbitrary pixels but the ratio will be kept.
        splitter.setSizes([300, 600])

        right_layout.addWidget(splitter)

        # store current video url and prompt user on startup after the window is shown
        self.current_video_url = ""
        # Use QTimer.singleShot to prompt after the event loop starts so the window is visible
        from PyQt6.QtCore import QTimer

        # If a match_id was provided, load the match metadata and events, and
        # avoid prompting for a startup video URL because the match may already
        # contain a video URL.
        if self.match_id:
            try:
                m = self.controller.get_match(self.match_id)
                if m and len(m) > 5 and m[5]:
                    # m[5] is video_url per schema: id, data, squadra_home, squadra_away, minuto_kickoff, video_url, name
                    self.current_video_url = m[5]
                    try:
                        self.video_player.set_url(self.current_video_url)
                    except Exception:
                        pass
                # populate the fixed fields from match so the filtered table loads correctly
                try:
                    if m and len(m) > 3:
                        self.data_input.setDate(QDate.fromString(m[1], "dd/MM/yyyy"))
                        self.squadra_home_input.setText(m[2])
                        self.squadra_away_input.setText(m[3])
                        # minuto_kickoff may be at index 4
                        if len(m) > 4 and m[4]:
                            self.minuto_kickoff_input.setText(m[4])
                except Exception:
                    pass

                eventi = self.controller.lista_eventi_per_match(self.match_id)
                self.table.setRowCount(0)
                for evento in eventi:
                    data = {
                        "data": evento[1],
                        "squadra_home": evento[2],
                        "squadra_away": evento[3],
                        "giocatore": evento[4],
                        "minuto": evento[5],
                        "minuto_kickoff": evento[6],
                        "tipo_fase": evento[7],
                        "evento_principale": evento[8],
                        "origine_possesso": evento[9],
                        "num_fasi": evento[10],
                        "zona": evento[11],
                        "esito": evento[12],
                        "linea_guadagno": evento[13],
                        "velocita_ruck": evento[14],
                        "penalita": evento[15],
                        "commento": evento[16],
                        "video_url": self._evento_video_url(evento),
                        "id": evento[0],
                    }
                    self.aggiungi_riga_tabella(data)
            except Exception:
                # fallback to prompting for a URL and loading filtered events
                QTimer.singleShot(0, self._prompt_for_video_url)
                self.carica_eventi_tabella()
        else:
            # No match selected at startup: prompt for a video URL and load filtered events
            QTimer.singleShot(0, self._prompt_for_video_url)
            self.carica_eventi_tabella()

    # ==========================
    # Form
    # ==========================
    def init_form(self, layout):
        self.data_input = QDateEdit()
        self.data_input.setDisplayFormat("dd/MM/yyyy")
        self.data_input.setDate(QDate.currentDate())

        self.squadra_home_input = QLineEdit()
        self.squadra_away_input = QLineEdit()
        self.minuto_kickoff_input = QLineEdit()
        self.giocatore_input = QLineEdit()

        fixed_labels = ["Data", "Squadra Home", "Squadra Away", "Minuto Kickoff"]
        fixed_widgets = [
            self.data_input,
            self.squadra_home_input,
            self.squadra_away_input,
            self.minuto_kickoff_input,
        ]

        grid = QGridLayout()
        layout.addLayout(grid)

        for i, (label_text, widget) in enumerate(zip(fixed_labels, fixed_widgets)):
            grid.addWidget(QLabel(label_text + ":"), i, 0)
            grid.addWidget(widget, i, 1)

        # --- Linea divisoria ---
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)

        # --- Campi variabili ---
        start_row = len(fixed_labels) + 1

        self.minuto_input = QLineEdit()
        self.video_url_input = QLineEdit()
        self.tipo_fase_input = QComboBox()
        self.tipo_fase_input.addItems(["Attacco", "Difesa", "Transizione"])

        self.evento_principale_input = QComboBox()
        self.evento_principale_input.addItems(
            [
                "Touche",
                "Mischia",
                "Ruck",
                "Maul",
                "Calcio",
                "Penalità",
                "Meta",
                "Turnover",
            ]
        )

        self.origine_possesso_input = QComboBox()
        self.origine_possesso_input.addItems(
            ["Touche", "Mischia", "Calcio", "Turnover", "Inizio tempo"]
        )

        self.num_fasi_input = QSpinBox()
        self.zona_input = QComboBox()
        self.zona_input.addItems(["22D", "50D", "50A", "22A"])

        self.esito_input = QComboBox()
        self.esito_input.addItems(["Neutro", "Negativo", "Positivo"])

        self.linea_guadagno_input = QComboBox()
        self.linea_guadagno_input.addItems(["Guadagnata", "Persa", "Neutra"])

        self.velocita_ruck_input = QComboBox()
        self.velocita_ruck_input.addItems(["", "Veloce", "Media", "Lenta"])

        self.penalita_input = QComboBox()
        self.penalita_input.addItems(["", "CP+", "CP-", "S+", "S-", "CL+", "CL-"])

        self.commento_input = QTextEdit()

        var_labels = [
            "Minuto",
            "Tipo fase",
            "Evento principale",
            "Origine possesso",
            "Numero fasi",
            "Zona",
            "Esito",
            "Linea guadagno",
            "Velocità ruck",
            "Penalità",
            "Commento",
            "Video URL",
        ]
        var_widgets = [
            self.minuto_input,
            self.tipo_fase_input,
            self.evento_principale_input,
            self.origine_possesso_input,
            self.num_fasi_input,
            self.zona_input,
            self.esito_input,
            self.linea_guadagno_input,
            self.velocita_ruck_input,
            self.penalita_input,
            self.commento_input,
            self.video_url_input,
        ]

        for i, (label_text, widget) in enumerate(
            zip(var_labels, var_widgets), start=start_row
        ):
            grid.addWidget(QLabel(label_text + ":"), i, 0)
            grid.addWidget(widget, i, 1)

    # ==========================
    # Funzioni principali
    # ==========================
    def salva_evento(self):
        # --- Verifica campi obbligatori ---
        if (
            not self.data_input.date().isValid()
            or not self.squadra_home_input.text().strip()
            or not self.squadra_away_input.text().strip()
            or not self.minuto_kickoff_input.text().strip()
        ):
            QMessageBox.warning(
                self,
                "Errore",
                "I campi Data, Squadra Home, Squadra Away e Minuto Kickoff sono obbligatori!",
            )
            return

        # --- Creazione dizionario evento ---
        data = {
            "data": self.data_input.date().toString("dd/MM/yyyy"),
            "squadra_home": self.squadra_home_input.text(),
            "squadra_away": self.squadra_away_input.text(),
            "giocatore": self.giocatore_input.text(),
            "minuto": self.minuto_input.text(),
            "video_url": self.video_url_input.text(),
            "minuto_kickoff": self.minuto_kickoff_input.text(),
            "tipo_fase": self.tipo_fase_input.currentText(),
            "evento_principale": self.evento_principale_input.currentText(),
            "origine_possesso": self.origine_possesso_input.currentText(),
            "num_fasi": self.num_fasi_input.value(),
            "zona": self.zona_input.currentText(),
            "esito": self.esito_input.currentText(),
            "linea_guadagno": self.linea_guadagno_input.currentText(),
            "velocita_ruck": self.velocita_ruck_input.currentText(),
            "penalita": self.penalita_input.currentText(),
            "commento": self.commento_input.toPlainText(),
        }

        # remove debug logging

        # If user didn't specify a video URL in the form, default to the currently loaded video
        if not data.get("video_url"):
            try:
                player_url = ""
                if hasattr(self.video_player, "get_current_url"):
                    player_url = self.video_player.get_current_url() or ""
                if not player_url:
                    player_url = self.current_video_url or ""
                if player_url:
                    data["video_url"] = player_url
            except Exception:
                pass

            # Validate video URL format (if present)
            if data.get("video_url") and not is_valid_youtube_url(
                str(data.get("video_url") or "")
            ):
                # show transient error and do not save
                QMessageBox.warning(
                    self,
                    "URL non valida",
                    "Il campo Video URL non sembra essere un link YouTube valido.",
                )
                return

        # If editing_evento_id is set AND we have a valid editing_row index,
        # perform UPDATE. Otherwise INSERT new.
        if (
            self.editing_evento_id is not None
            and self.editing_row is not None
            and self.editing_row >= 0
        ):
            evento_id = self.editing_evento_id
            try:
                self.controller.modifica_evento(evento_id, data)
                data["id"] = evento_id
                try:
                    self.aggiorna_riga_tabella(self.editing_row, data)
                except Exception:
                    pass
            except Exception as e:
                QMessageBox.warning(
                    self, "Errore", f"Impossibile aggiornare evento: {e}"
                )
            finally:
                # reset edit state and restore save button
                try:
                    self.editing_row = -1
                    self.editing_evento_id = None
                    if hasattr(self, "save_button"):
                        self.save_button.setText("Salva Evento")
                        self.save_button.setStyleSheet("")
                except Exception:
                    pass
        else:
            try:
                evento_id = self.controller.salva_evento(data)
                data["id"] = evento_id
            except Exception as e:
                QMessageBox.warning(self, "Errore", f"Impossibile salvare evento: {e}")
                return

            # Decide whether the inserted event matches current filters. Read
            # filters BEFORE we clear the form so we compare accurately.
            try:
                data_fissa = self.data_input.date().toString("dd/MM/yyyy")
                squadra_home = self.squadra_home_input.text()
                squadra_away = self.squadra_away_input.text()
                minuto_kickoff = self.minuto_kickoff_input.text()
                inserted_matches = (
                    data["data"] == data_fissa
                    and data["squadra_home"] == squadra_home
                    and data["squadra_away"] == squadra_away
                    and data.get("minuto_kickoff", "") == minuto_kickoff
                )
            except Exception:
                inserted_matches = False

            if inserted_matches:
                try:
                    self.aggiungi_riga_tabella(data)
                except Exception:
                    try:
                        self.carica_eventi_tabella()
                    except Exception:
                        pass
            else:
                try:
                    self.carica_eventi_tabella()
                except Exception:
                    pass

        # --- Pulisci solo campi variabili ---
        self.pulisci_form_variabili()

    def pulisci_form_variabili(self):
        self.giocatore_input.clear()
        self.minuto_input.clear()
        self.video_url_input.clear()
        self.tipo_fase_input.setCurrentIndex(0)
        self.evento_principale_input.setCurrentIndex(0)
        self.origine_possesso_input.setCurrentIndex(0)
        self.num_fasi_input.setValue(0)
        self.zona_input.setCurrentIndex(0)
        self.esito_input.setCurrentIndex(0)
        self.linea_guadagno_input.setCurrentIndex(0)
        self.velocita_ruck_input.setCurrentIndex(0)
        self.penalita_input.setCurrentIndex(0)
        self.commento_input.clear()
        # Clear any edit state and restore Save button label
        try:
            self.editing_row = -1
            self.editing_evento_id = None
            if hasattr(self, "save_button"):
                self.save_button.setText("Salva Evento")
        except Exception:
            pass

    def save_match(self):
        """
        Save the current session as a Match and link events matching the current
        fixed filters (data, squadra_home, squadra_away, minuto_kickoff) to it.
        """
        # Collect match metadata from current fixed fields
        match = {
            "data": self.data_input.date().toString("dd/MM/yyyy"),
            "squadra_home": self.squadra_home_input.text(),
            "squadra_away": self.squadra_away_input.text(),
            "minuto_kickoff": self.minuto_kickoff_input.text(),
            "video_url": self.current_video_url or "",
            "name": f"{self.squadra_home_input.text()} vs {self.squadra_away_input.text()} {self.data_input.date().toString('dd/MM/yyyy')}",
        }
        try:
            if self.match_id:
                # update existing match
                updated = self.controller.modifica_match(self.match_id, match)
                # relink events (in case fixed fields changed)
                linked = self.controller.link_events_to_match(
                    self.match_id,
                    match["data"],
                    match["squadra_home"],
                    match["squadra_away"],
                    match["minuto_kickoff"],
                )
                QMessageBox.information(
                    self,
                    "Match Updated",
                    f"Match id={self.match_id} updated. Linked {linked} events.",
                )
            else:
                match_id = self.controller.salva_match(match)
                # Link existing events for the current fixed filters to this match
                updated = self.controller.link_events_to_match(
                    match_id,
                    match["data"],
                    match["squadra_home"],
                    match["squadra_away"],
                    match["minuto_kickoff"],
                )
                QMessageBox.information(
                    self,
                    "Match Saved",
                    f"Match saved id={match_id}. Linked {updated} events.",
                )
                # remember current match id
                self.match_id = match_id
        except Exception as e:
            QMessageBox.warning(self, "Errore", f"Impossibile salvare match: {e}")

    def change_match(self):
        """Show the MatchSelector to pick or create a match, then reload events."""
        try:
            from ui.match_selector import MatchSelector

            selector = MatchSelector(self)
            from PyQt6.QtWidgets import QDialog as _QDialog

            if selector.exec() == _QDialog.DialogCode.Accepted:
                sel = selector.selected_match_id
                if sel:
                    self.match_id = sel
                    # load match metadata and populate fixed fields
                    try:
                        m = self.controller.get_match(self.match_id)
                        if m and len(m) > 3:
                            try:
                                self.data_input.setDate(
                                    QDate.fromString(m[1], "dd/MM/yyyy")
                                )
                            except Exception:
                                pass
                            self.squadra_home_input.setText(m[2] or "")
                            self.squadra_away_input.setText(m[3] or "")
                            if len(m) > 4:
                                self.minuto_kickoff_input.setText(m[4] or "")
                            if len(m) > 5 and m[5]:
                                self.current_video_url = m[5]
                                try:
                                    self.video_player.set_url(self.current_video_url)
                                except Exception:
                                    pass
                    except Exception:
                        pass
                    # reload events for the selected match
                    try:
                        self.table.setRowCount(0)
                        eventi = self.controller.lista_eventi_per_match(self.match_id)
                        for evento in eventi:
                            data = {
                                "data": evento[1],
                                "squadra_home": evento[2],
                                "squadra_away": evento[3],
                                "giocatore": evento[4],
                                "minuto": evento[5],
                                "minuto_kickoff": evento[6],
                                "tipo_fase": evento[7],
                                "evento_principale": evento[8],
                                "origine_possesso": evento[9],
                                "num_fasi": evento[10],
                                "zona": evento[11],
                                "esito": evento[12],
                                "linea_guadagno": evento[13],
                                "velocita_ruck": evento[14],
                                "penalita": evento[15],
                                "commento": evento[16],
                                "video_url": self._evento_video_url(evento),
                                "id": evento[0],
                            }
                            self.aggiungi_riga_tabella(data)
                    except Exception:
                        self.carica_eventi_tabella()
        except Exception:
            pass

    def _table_text(self, row: int, col: int) -> str:
        """Safely return the text of a QTableWidget cell or empty string.

        Central helper to avoid calling .text() on None.
        """
        item = self.table.item(row, col)
        if item is None:
            return ""
        txt = item.text()
        return txt if txt is not None else ""

    def _evento_video_url(self, evento) -> str:
        """Robustly extract a video_url from an evento row tuple.

        Some databases may have different column ordering depending on
        migrations. Prefer index 17, then 16, else empty string.
        """
        try:
            if evento is None:
                return ""
            if len(evento) > 17 and evento[17]:
                return evento[17]
            if len(evento) > 16 and evento[16]:
                return evento[16]
        except Exception:
            pass
        return ""

    # ==========================
    # Tabella e menu contestuale
    # ==========================
    def menu_contenstuale(self, pos: QPoint):
        index = self.table.indexAt(pos)
        if not index.isValid():
            return
        row = index.row()
        menu = QMenu()
        modifica_action = menu.addAction("Modifica")
        elimina_action = menu.addAction("Elimina")
        vp = self.table.viewport()
        if vp is not None:
            action = menu.exec(vp.mapToGlobal(pos))
        else:
            action = menu.exec(self.table.mapToGlobal(pos))
        if action == elimina_action:
            self.elimina_riga(row)
        elif action == modifica_action:
            self.carica_form_per_modifica(row)

    def elimina_riga(self, row):
        confirm = QMessageBox.question(
            self,
            "Conferma",
            "Eliminare l'evento selezionato?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirm == QMessageBox.StandardButton.Yes:
            # ID shifted to column 17
            evento_id = self._table_text(row, 17)
            self.controller.elimina_evento(evento_id)
            self.table.removeRow(row)

    def carica_form_per_modifica(self, row):
        self.editing_row = row
        # Store the DB id for the event being edited (ID at column 17)
        try:
            id_text = self._table_text(row, 17)
            self.editing_evento_id = int(id_text) if id_text else None
        except Exception:
            self.editing_evento_id = None
        # Visual cue: set save button into edit mode
        try:
            if hasattr(self, "save_button"):
                self.save_button.setText("Aggiorna Evento")
                self.save_button.setStyleSheet(
                    "background-color: #fff3cd; color: #856404;"
                )
        except Exception:
            pass
        # Columns: 0=Data,1=Squadra Home,2=Squadra Away,3=Giocatore,4=Minuto Kickoff,
        # 5=Minuto,6=Tipo fase,7=Evento principale,8=Origine possesso,9=Num fasi,...
        self.giocatore_input.setText(self._table_text(row, 3))
        self.minuto_kickoff_input.setText(self._table_text(row, 4))
        self.minuto_input.setText(self._table_text(row, 5))
        self.tipo_fase_input.setCurrentText(self._table_text(row, 6))
        self.evento_principale_input.setCurrentText(self._table_text(row, 7))
        self.origine_possesso_input.setCurrentText(self._table_text(row, 8))

        # num_fasi might be empty; guard conversion
        num_fasi_txt = self._table_text(row, 9)
        try:
            self.num_fasi_input.setValue(int(num_fasi_txt) if num_fasi_txt else 0)
        except Exception:
            self.num_fasi_input.setValue(0)
        self.zona_input.setCurrentText(self._table_text(row, 10))
        self.esito_input.setCurrentText(self._table_text(row, 11))
        self.linea_guadagno_input.setCurrentText(self._table_text(row, 12))
        self.velocita_ruck_input.setCurrentText(self._table_text(row, 13))
        self.penalita_input.setCurrentText(self._table_text(row, 14))
        self.commento_input.setPlainText(self._table_text(row, 15))
        # Video URL is in column 16
        self.video_url_input.setText(self._table_text(row, 16))

    def carica_eventi_tabella(self):
        """Carica solo gli eventi che hanno stessi campi fissi della sessione corrente"""
        self.table.setRowCount(0)
        data_fissa = self.data_input.date().toString("dd/MM/yyyy")
        squadra_home = self.squadra_home_input.text()
        squadra_away = self.squadra_away_input.text()
        minuto_kickoff = self.minuto_kickoff_input.text()

        eventi = self.controller.lista_eventi_filtrati(
            data_fissa, squadra_home, squadra_away, minuto_kickoff
        )
        for evento in eventi:
            data = {
                "data": evento[1],
                "squadra_home": evento[2],
                "squadra_away": evento[3],
                "giocatore": evento[4],
                "minuto": evento[5],
                "minuto_kickoff": evento[6],
                "tipo_fase": evento[7],
                "evento_principale": evento[8],
                "origine_possesso": evento[9],
                "num_fasi": evento[10],
                "zona": evento[11],
                "esito": evento[12],
                "linea_guadagno": evento[13],
                "velocita_ruck": evento[14],
                "penalita": evento[15],
                "commento": evento[16],
                "video_url": self._evento_video_url(evento),
                "id": evento[0],
            }
            self.aggiungi_riga_tabella(data)

    def aggiungi_riga_tabella(self, data):
        row_pos = self.table.rowCount()
        self.table.insertRow(row_pos)
        self.aggiorna_riga_tabella(row_pos, data)

    def aggiorna_riga_tabella(self, row, data):
        values = [
            data["data"],
            data["squadra_home"],
            data["squadra_away"],
            data.get("giocatore", ""),
            data.get("minuto_kickoff", ""),
            data.get("minuto", ""),
            data.get("tipo_fase", ""),
            data.get("evento_principale", ""),
            data.get("origine_possesso", ""),
            str(data.get("num_fasi", "")),
            data.get("zona", ""),
            data.get("esito", ""),
            data.get("linea_guadagno", ""),
            data.get("velocita_ruck", ""),
            data.get("penalita", ""),
            data.get("commento", ""),
            data.get("video_url", ""),
            str(data["id"]),
        ]
        for col, value in enumerate(values):
            self.table.setItem(row, col, QTableWidgetItem(str(value)))

    def switch_video_player(self, mode: str) -> None:
        """
        Switch the video player implementation at runtime.

        Args:
            mode: "embed" to use [`VideoPlayerEmbed`](app/ui/video_player_embed.py)
                  or "stream" to use [`VideoPlayerStream`](app/ui/video_player_stream.py).
        """
        if mode == self.current_video_mode:
            return

        # Remove and delete existing widget(s) inside the container
        while self.video_container_layout.count():
            item = self.video_container_layout.takeAt(0)
            if item is None:
                continue
            widget = item.widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()

        # Instantiate the requested player
        if mode == "embed":
            new_player = VideoPlayerEmbed(self)
        else:
            new_player = VideoPlayerStream(self)
        # Ensure the new player expands to fill the video container
        try:
            new_player.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
            )
        except Exception:
            pass

        self.video_player = new_player
        self.video_container_layout.addWidget(self.video_player)
        self.current_video_mode = mode

        # Try to reload the current video URL (fallback to demo if not present)
        url_to_load = (
            self.current_video_url or "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        )
        try:
            try:
                self.video_player.set_url(url_to_load, 0)
            except TypeError:
                self.video_player.set_url(url_to_load)
        except Exception:
            # Keep UI stable if player doesn't accept set_url or fails
            pass

    def on_table_cell_clicked(self, row: int, column: int) -> None:
        """Handle table clicks: load/seek the video to the time specified in the 'Minuto' column.

        The 'Minuto' column is at index 4. It may contain a minute value (int) or a time
        string like '1:23' meaning 1 minute 23 seconds. We convert that to milliseconds
        and instruct the current video player to seek to that position.
        """
        # Minuto now lives in column 5 (after inserting 'Giocatore' and 'Minuto Kickoff')
        minuto_item = self.table.item(row, 5)
        if minuto_item is None:
            return
        minuto_text = minuto_item.text().strip() if minuto_item.text() else ""
        if not minuto_text:
            return
        ms = parse_minuto_to_ms(minuto_text)

        # Prefer the per-row video URL (col 16). Fallback to currently loaded URL or demo.
        row_video_url = self._table_text(row, 16)
        demo = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        url = row_video_url or self.current_video_url or demo

        # If the currently loaded player's URL is different from the row's URL,
        # load the row URL (with start) instead of only calling seek(). This
        # fixes the embed player behavior where seek() is a no-op if no URL
        # was previously loaded.
        current_player_url = ""
        try:
            if hasattr(self.video_player, "get_current_url"):
                current_player_url = self.video_player.get_current_url() or ""
        except Exception:
            current_player_url = self.current_video_url or ""

        # If player doesn't have the event's URL loaded, set it (with start)
        try:
            if not current_player_url or (
                row_video_url and row_video_url != current_player_url
            ):
                try:
                    try:
                        self.video_player.set_url(url, ms)
                    except TypeError:
                        self.video_player.set_url(url)
                except Exception:
                    pass
                try:
                    if hasattr(self.video_player, "play"):
                        self.video_player.play()
                except Exception:
                    pass
                return
        except Exception:
            # fall back to seek below
            pass

        # Otherwise the player already has the correct URL -> attempt to seek.
        try:
            if hasattr(self.video_player, "seek"):
                try:
                    self.video_player.seek(ms)
                except Exception:
                    # If seek fails, try loading the URL at the desired position
                    try:
                        try:
                            self.video_player.set_url(url, ms)
                        except TypeError:
                            self.video_player.set_url(url)
                    except Exception:
                        pass
                # Attempt to start playback after seeking/loading
                try:
                    if hasattr(self.video_player, "play"):
                        self.video_player.play()
                except Exception:
                    pass
                return
        except Exception:
            pass

        # Last-resort: set the URL and play
        try:
            try:
                self.video_player.set_url(url, ms)
            except TypeError:
                self.video_player.set_url(url)
            try:
                if hasattr(self.video_player, "play"):
                    self.video_player.play()
            except Exception:
                pass
        except Exception:
            # give up silently
            pass

    def _parse_minuto_to_ms(self, text: str) -> int:
        # Deprecated: use core.utils.parse_minuto_to_ms
        return parse_minuto_to_ms(text)

    def _prompt_for_video_url(self) -> None:
        """
        Prompt the user for a YouTube URL on startup. Stores the result in
        `self.current_video_url` and loads it into the active video player.

        If the user cancels or provides an empty value, a demo URL is used.
        """
        demo = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        text, ok = QInputDialog.getText(
            self, "Enter YouTube Video URL:", "Enter YouTube Video URL:"
        )
        if not ok or not text or not text.strip():
            self.current_video_url = demo
        else:
            val = text.strip()
            if is_valid_youtube_url(val):
                self.current_video_url = val
            else:
                # keep demo but show a small non-blocking hint in the form
                self.current_video_url = demo
                try:
                    self.status_label.setText(
                        "Invalid YouTube URL provided at startup; using demo video."
                    )
                except Exception:
                    pass

        # Attempt to load into the current player
        try:
            self.video_player.set_url(self.current_video_url)
        except Exception:
            # If loading fails, show a non-blocking label in the video container
            # If the player supports an info label internally it will show errors;
            # otherwise we add a small QLabel here.
            try:
                info_label = QLabel(f"Unable to load URL: {self.current_video_url}")
                self.video_container_layout.addWidget(info_label)
            except Exception:
                pass

    def add_video(self) -> None:
        """
        Prompt the user to add/set a video URL. Prefills the dialog with the
        currently loaded player's URL (if available) or the stored current_video_url.
        On accept, updates the player and the Video URL form field.
        """
        prefill = ""
        try:
            if hasattr(self.video_player, "get_current_url"):
                prefill = self.video_player.get_current_url() or ""
        except Exception:
            prefill = self.current_video_url or ""

        text, ok = QInputDialog.getText(
            self, "Add Video URL", "Video URL:", text=prefill
        )
        if not ok:
            return
        url = text.strip() if text else ""
        if not url:
            return

        if not is_valid_youtube_url(url):
            # transient UI feedback
            try:
                self.status_label.setText(
                    "Please enter a valid YouTube URL (youtube.com/watch?v=... or youtu.be/...)."
                )
            except Exception:
                pass
            return

        # Update form field
        try:
            self.video_url_input.setText(url)
        except Exception:
            pass

        # Try to load into player (normalized API)
        try:
            try:
                self.video_player.set_url(url, 0)
            except TypeError:
                self.video_player.set_url(url)
        except Exception:
            # ignore errors; player may not support set_url
            pass
