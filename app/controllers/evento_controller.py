from core import services


class EventoController:
    def salva_evento(self, data):
        return services.salva_evento(data)

    def modifica_evento(self, evento_id, data):
        services.modifica_evento(evento_id, data)

    def elimina_evento(self, evento_id):
        services.elimina_evento(evento_id)

    def lista_eventi_filtrati(self, data, squadra_home, squadra_away, minuto_kickoff):
        return services.lista_eventi_filtrati(
            data, squadra_home, squadra_away, minuto_kickoff
        )

    # Match related
    def salva_match(self, match):
        return services.salva_match(match)

    def lista_matches(self):
        return services.lista_matches()

    def get_match(self, match_id):
        return services.get_match(match_id)

    def lista_eventi_per_match(self, match_id):
        return services.lista_eventi_per_match(match_id)

    def link_events_to_match(
        self, match_id, data, squadra_home, squadra_away, minuto_kickoff
    ):
        return services.link_events_to_match(
            match_id, data, squadra_home, squadra_away, minuto_kickoff
        )

    def modifica_match(self, match_id, match):
        return services.modifica_match(match_id, match)

    def elimina_match(self, match_id):
        return services.elimina_match(match_id)
