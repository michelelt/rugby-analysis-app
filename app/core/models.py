from dataclasses import dataclass

@dataclass
class Evento:
    data: str
    squadra_home: str
    squadra_away: str
    giocatore: str
    minuto: str               # minuto dell'evento, variabile
    minuto_kickoff: str       # minuto del fischio iniziale, fisso
    tipo_fase: str
    evento_principale: str
    origine_possesso: str
    num_fasi: int
    zona: str
    esito: str
    linea_guadagno: str
    velocita_ruck: str
    penalita: str
    commento: str
