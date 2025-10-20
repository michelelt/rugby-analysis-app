from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTextEdit, QSpinBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QGridLayout, QMenu, QMessageBox, QComboBox, QDateEdit, QFrame
)
from PyQt6.QtCore import Qt, QPoint, QDate
from controllers.evento_controller import EventoController


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Analisi Rugby")
        self.setGeometry(100, 100, 1500, 700)
        self.controller = EventoController()
        self.editing_row = None

        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        # --- Lato sinistro: form ---
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_widget.setLayout(left_layout)
        main_layout.addWidget(left_widget, 3)

        self.init_form(left_layout)
        save_button = QPushButton("Salva Evento")
        save_button.clicked.connect(self.salva_evento)
        left_layout.addWidget(save_button)

        # --- Lato destro: tabella ---
        self.table = QTableWidget()
        self.table.setColumnCount(16)
        self.table.setHorizontalHeaderLabels([
            "Data", "Squadra Home", "Squadra Away", "Minuto Kickoff",
            "Minuto", "Tipo fase", "Evento principale", "Origine possesso",
            "Num fasi", "Zona", "Esito", "Linea guadagno", "Velocità ruck",
            "Penalità", "Commento", "ID"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.menu_contenstuale)
        main_layout.addWidget(self.table, 5)

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
        fixed_widgets = [self.data_input, self.squadra_home_input, self.squadra_away_input, self.minuto_kickoff_input]

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
        self.tipo_fase_input = QComboBox()
        self.tipo_fase_input.addItems(["Attacco", "Difesa", "Transizione"])

        self.evento_principale_input = QComboBox()
        self.evento_principale_input.addItems([
            "Touche", "Mischia", "Ruck", "Maul", "Calcio", "Penalità", "Meta", "Turnover"
        ])

        self.origine_possesso_input = QComboBox()
        self.origine_possesso_input.addItems(["Touche", "Mischia", "Calcio", "Turnover", "Inizio tempo"])

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

        var_labels = ["Minuto", "Tipo fase", "Evento principale", "Origine possesso",
                      "Numero fasi", "Zona", "Esito", "Linea guadagno", "Velocità ruck",
                      "Penalità", "Commento"]
        var_widgets = [self.minuto_input, self.tipo_fase_input, self.evento_principale_input,
                       self.origine_possesso_input, self.num_fasi_input, self.zona_input,
                       self.esito_input, self.linea_guadagno_input, self.velocita_ruck_input,
                       self.penalita_input, self.commento_input]

        for i, (label_text, widget) in enumerate(zip(var_labels, var_widgets), start=start_row):
            grid.addWidget(QLabel(label_text + ":"), i, 0)
            grid.addWidget(widget, i, 1)

    # ==========================
    # Funzioni principali
    # ==========================
    def salva_evento(self):
        # --- Verifica campi obbligatori ---
        if not self.data_input.date().isValid() or \
           not self.squadra_home_input.text().strip() or \
           not self.squadra_away_input.text().strip() or \
           not self.minuto_kickoff_input.text().strip():
            QMessageBox.warning(
                self, "Errore",
                "I campi Data, Squadra Home, Squadra Away e Minuto Kickoff sono obbligatori!"
            )
            return

        # --- Creazione dizionario evento ---
        data = {
            "data": self.data_input.date().toString("dd/MM/yyyy"),
            "squadra_home": self.squadra_home_input.text(),
            "squadra_away": self.squadra_away_input.text(),
            "giocatore": self.giocatore_input.text(),
            "minuto": self.minuto_input.text(),
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
            "commento": self.commento_input.toPlainText()
        }

        if self.editing_row is not None:
            evento_id = self.table.item(self.editing_row, 15).text()
            self.controller.modifica_evento(evento_id, data)
            self.aggiorna_riga_tabella(self.editing_row, data)
            self.editing_row = None
        else:
            evento_id = self.controller.salva_evento(data)
            data["id"] = evento_id
            self.aggiungi_riga_tabella(data)

        # --- Pulisci solo campi variabili ---
        self.pulisci_form_variabili()
        # --- Ricarica solo eventi filtrati ---
        self.carica_eventi_tabella()

    def pulisci_form_variabili(self):
        self.giocatore_input.clear()
        self.minuto_input.clear()
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
        action = menu.exec(self.table.viewport().mapToGlobal(pos))
        if action == elimina_action:
            self.elimina_riga(row)
        elif action == modifica_action:
            self.carica_form_per_modifica(row)

    def elimina_riga(self, row):
        confirm = QMessageBox.question(
            self, "Conferma", "Eliminare l'evento selezionato?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            evento_id = self.table.item(row, 15).text()
            self.controller.elimina_evento(evento_id)
            self.table.removeRow(row)

    def carica_form_per_modifica(self, row):
        self.editing_row = row
        self.giocatore_input.setText(self.table.item(row, 4).text())
        self.minuto_input.setText(self.table.item(row, 4).text())
        self.tipo_fase_input.setCurrentText(self.table.item(row, 5).text())
        self.evento_principale_input.setCurrentText(self.table.item(row, 6).text())
        self.origine_possesso_input.setCurrentText(self.table.item(row, 7).text())
        self.num_fasi_input.setValue(int(self.table.item(row, 8).text()))
        self.zona_input.setCurrentText(self.table.item(row, 9).text())
        self.esito_input.setCurrentText(self.table.item(row, 10).text())
        self.linea_guadagno_input.setCurrentText(self.table.item(row, 11).text())
        self.velocita_ruck_input.setCurrentText(self.table.item(row, 12).text())
        self.penalita_input.setCurrentText(self.table.item(row, 13).text())
        self.commento_input.setPlainText(self.table.item(row, 14).text())

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
                "id": evento[0]
            }
            self.aggiungi_riga_tabella(data)

    def aggiungi_riga_tabella(self, data):
        row_pos = self.table.rowCount()
        self.table.insertRow(row_pos)
        self.aggiorna_riga_tabella(row_pos, data)

    def aggiorna_riga_tabella(self, row, data):
        values = [
            data["data"], data["squadra_home"], data["squadra_away"], data["minuto_kickoff"],
            data["minuto"], data["tipo_fase"], data["evento_principale"], data["origine_possesso"],
            str(data["num_fasi"]), data["zona"], data["esito"], data["linea_guadagno"],
            data["velocita_ruck"], data["penalita"], data["commento"], str(data["id"])
        ]
        for col, value in enumerate(values):
            self.table.setItem(row, col, QTableWidgetItem(str(value)))
