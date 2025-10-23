from core.database import get_connection


def salva_evento(evento):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        """
        INSERT INTO eventi
        (data, squadra_home, squadra_away, giocatore, minuto, minuto_kickoff, tipo_fase,
         evento_principale, origine_possesso, num_fasi, zona, esito, linea_guadagno,
         velocita_ruck, penalita, commento, video_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            evento["data"],
            evento["squadra_home"],
            evento["squadra_away"],
            evento["giocatore"],
            evento["minuto"],
            evento["minuto_kickoff"],
            evento["tipo_fase"],
            evento["evento_principale"],
            evento["origine_possesso"],
            evento["num_fasi"],
            evento["zona"],
            evento["esito"],
            evento["linea_guadagno"],
            evento["velocita_ruck"],
            evento["penalita"],
            evento["commento"],
            evento.get("video_url", ""),
        ),
    )
    conn.commit()
    evento_id = c.lastrowid
    conn.close()
    try:
        print(f"[DB] INSERT evento id={evento_id} data={evento}")
    except Exception:
        pass
    return evento_id


def modifica_evento(evento_id, evento):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        """
        UPDATE eventi SET
            giocatore=?, minuto=?, tipo_fase=?, evento_principale=?, origine_possesso=?,
            num_fasi=?, zona=?, esito=?, linea_guadagno=?, velocita_ruck=?, penalita=?, commento=?, video_url=?
        WHERE id=?
    """,
        (
            evento["giocatore"],
            evento["minuto"],
            evento["tipo_fase"],
            evento["evento_principale"],
            evento["origine_possesso"],
            evento["num_fasi"],
            evento["zona"],
            evento["esito"],
            evento["linea_guadagno"],
            evento["velocita_ruck"],
            evento["penalita"],
            evento["commento"],
            evento.get("video_url", ""),
            evento_id,
        ),
    )
    conn.commit()
    conn.close()
    try:
        print(f"[DB] UPDATE evento id={evento_id} data={evento}")
    except Exception:
        pass


def elimina_evento(evento_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM eventi WHERE id=?", (evento_id,))
    conn.commit()
    conn.close()


def lista_eventi_filtrati(data, squadra_home, squadra_away, minuto_kickoff):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        """
        SELECT * FROM eventi
        WHERE data=? AND squadra_home=? AND squadra_away=? AND minuto_kickoff=?
        ORDER BY id DESC
    """,
        (data, squadra_home, squadra_away, minuto_kickoff),
    )
    eventi = c.fetchall()
    conn.close()
    return eventi


def salva_match(match):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        """
        INSERT INTO matches (data, squadra_home, squadra_away, minuto_kickoff, video_url, name)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
        (
            match.get("data"),
            match.get("squadra_home"),
            match.get("squadra_away"),
            match.get("minuto_kickoff"),
            match.get("video_url"),
            match.get("name"),
        ),
    )
    conn.commit()
    match_id = c.lastrowid
    conn.close()
    return match_id


def modifica_match(match_id, match):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        """
        UPDATE matches SET data=?, squadra_home=?, squadra_away=?, minuto_kickoff=?, video_url=?, name=?
        WHERE id=?
    """,
        (
            match.get("data"),
            match.get("squadra_home"),
            match.get("squadra_away"),
            match.get("minuto_kickoff"),
            match.get("video_url"),
            match.get("name"),
            match_id,
        ),
    )
    conn.commit()
    updated = c.rowcount
    conn.close()
    return updated


def elimina_match(match_id):
    conn = get_connection()
    c = conn.cursor()
    # unlink events first (optional): set match_id NULL
    c.execute("UPDATE eventi SET match_id=NULL WHERE match_id=?", (match_id,))
    c.execute("DELETE FROM matches WHERE id=?", (match_id,))
    conn.commit()
    deleted = c.rowcount
    conn.close()
    return deleted


def lista_matches():
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT id, name, data, squadra_home, squadra_away FROM matches ORDER BY id DESC"
    )
    rows = c.fetchall()
    conn.close()
    return rows


def get_match(match_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM matches WHERE id=?", (match_id,))
    m = c.fetchone()
    conn.close()
    return m


def lista_eventi_per_match(match_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM eventi WHERE match_id=? ORDER BY id DESC", (match_id,))
    rows = c.fetchall()
    conn.close()
    return rows


def link_events_to_match(match_id, data, squadra_home, squadra_away, minuto_kickoff):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        """
        UPDATE eventi SET match_id=?
        WHERE data=? AND squadra_home=? AND squadra_away=? AND minuto_kickoff=?
    """,
        (match_id, data, squadra_home, squadra_away, minuto_kickoff),
    )
    conn.commit()
    updated = c.rowcount
    conn.close()
    return updated
