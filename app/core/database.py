import sqlite3

DB_NAME = "analisi_rugby.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS eventi (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data TEXT,
        squadra_home TEXT,
        squadra_away TEXT,
        giocatore TEXT,
        minuto TEXT,
        minuto_kickoff TEXT,
        tipo_fase TEXT,
        evento_principale TEXT,
        origine_possesso TEXT,
        num_fasi INTEGER,
        zona TEXT,
        esito TEXT,
        linea_guadagno TEXT,
        velocita_ruck TEXT,
        penalita TEXT,
        commento TEXT
    )
    """)
    conn.commit()
    conn.close()
