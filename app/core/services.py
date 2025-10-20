from core.database import get_connection

def salva_evento(evento):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO eventi
        (data, squadra_home, squadra_away, giocatore, minuto, minuto_kickoff, tipo_fase,
         evento_principale, origine_possesso, num_fasi, zona, esito, linea_guadagno,
         velocita_ruck, penalita, commento)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        evento["data"], evento["squadra_home"], evento["squadra_away"], evento["giocatore"],
        evento["minuto"], evento["minuto_kickoff"], evento["tipo_fase"], evento["evento_principale"],
        evento["origine_possesso"], evento["num_fasi"], evento["zona"], evento["esito"],
        evento["linea_guadagno"], evento["velocita_ruck"], evento["penalita"], evento["commento"]
    ))
    conn.commit()
    evento_id = c.lastrowid
    conn.close()
    return evento_id

def modifica_evento(evento_id, evento):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        UPDATE eventi SET
            giocatore=?, minuto=?, tipo_fase=?, evento_principale=?, origine_possesso=?,
            num_fasi=?, zona=?, esito=?, linea_guadagno=?, velocita_ruck=?, penalita=?, commento=?
        WHERE id=?
    """, (
        evento["giocatore"], evento["minuto"], evento["tipo_fase"], evento["evento_principale"],
        evento["origine_possesso"], evento["num_fasi"], evento["zona"], evento["esito"],
        evento["linea_guadagno"], evento["velocita_ruck"], evento["penalita"], evento["commento"],
        evento_id
    ))
    conn.commit()
    conn.close()

def elimina_evento(evento_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM eventi WHERE id=?", (evento_id,))
    conn.commit()
    conn.close()

def lista_eventi_filtrati(data, squadra_home, squadra_away, minuto_kickoff):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT * FROM eventi
        WHERE data=? AND squadra_home=? AND squadra_away=? AND minuto_kickoff=?
        ORDER BY id DESC
    """, (data, squadra_home, squadra_away, minuto_kickoff))
    eventi = c.fetchall()
    conn.close()
    return eventi
