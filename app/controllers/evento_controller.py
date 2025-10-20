from core import services

class EventoController:
    def salva_evento(self, data):
        return services.salva_evento(data)

    def modifica_evento(self, evento_id, data):
        services.modifica_evento(evento_id, data)

    def elimina_evento(self, evento_id):
        services.elimina_evento(evento_id)

    def lista_eventi_filtrati(self, data, squadra_home, squadra_away, minuto_kickoff):
        return services.lista_eventi_filtrati(data, squadra_home, squadra_away, minuto_kickoff)
