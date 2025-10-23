import sqlite3

DB_NAME = "analisi_rugby.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        """
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
        commento TEXT,
        video_url TEXT,
        match_id INTEGER
    )
    """
    )
    # If the table exists but the column 'video_url' was added later, ensure the column exists.
    try:
        c.execute("PRAGMA table_info(eventi)")
        cols = [r[1] for r in c.fetchall()]
        if "video_url" not in cols:
            c.execute("ALTER TABLE eventi ADD COLUMN video_url TEXT")
        if "match_id" not in cols:
            c.execute("ALTER TABLE eventi ADD COLUMN match_id INTEGER")
        conn.commit()
    except Exception:
        # Don't fail initialization on migration issues; leave DB as-is
        pass

    # Ensure matches table exists
    try:
        c.execute(
            """
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            squadra_home TEXT,
            squadra_away TEXT,
            minuto_kickoff TEXT,
            video_url TEXT,
            name TEXT
        )
        """
        )
        conn.commit()
    except Exception:
        pass
    conn.commit()
    conn.close()
