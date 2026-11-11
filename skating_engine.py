# skating_engine.py

DISCIPLINE_PREDEFINITE = {
    "Danze Standard": ["Valzer Lento", "Tango", "Valzer Viennese", "Slow Fox", "Quickstep"],
    "Danze Latino-Americane": ["Samba", "Cha Cha Cha", "Rumba", "Paso Doble", "Jive"],
    "Danze Caraibiche": ["Salsa Cubana", "Salsa Portoricana", "Bachata", "Merengue"],
    "Ballo Liscio & Sala": ["Mazurka", "Valzer", "Polka", "Fox Trot"]
}

class SkatingEngine:
    def __init__(self, num_giudici):
        self.num_giudici = num_giudici
        self.maggioranza = (num_giudici // 2) + 1

    def calcola_passaggi_eliminatorie(self, voti_crocette, posti_disponibili=6):
        totale_crocette = {}
        for id_c, balli in voti_crocette.items():
            totale = sum(sum(1 for v in scelte if v) for scelte in balli.values())
            totale_crocette[id_c] = totale
            
        coppie_ordinate = sorted(totale_crocette.items(), key=lambda x: x[1], reverse=True)
        finalisti = [id_c for id_c, _ in coppie_ordinate[:posti_disponibili]]
        return finalisti, totale_crocette

    def calcola_singolo_ballo(self, voti_coppie):
        classifica = {}
        num_finalisti = len(voti_coppie)
        
        for pos in range(1, num_finalisti + 1):
            miglior_coppia = None
            max_voti = -1
            
            for id_c, voti in voti_coppie.items():
                if id_c in classifica.values():
                    continue
                voti_validi = sum(1 for v in voti if v <= pos)
                if voti_validi >= self.maggioranza and voti_validi > max_voti:
                    max_voti = voti_validi
                    miglior_coppia = id_c
            
            if miglior_coppia:
                classifica[pos] = miglior_coppia
            else:
                rimanenti = [id_c for id_c in voti_coppie if id_c not in classifica.values()]
                if rimanenti: classifica[pos] = rimanenti[0]
        return classifica

    def calcola_combinata(self, risultati_balli):
        punteggi_totali = {}
        tutti_i_piazzamenti = {}
        for ballo, classifica in risultati_balli.items():
            for pos, id_c in classifica.items():
                punteggi_totali[id_c] = punteggi_totali.get(id_c, 0) + pos
                tutti_i_piazzamenti.setdefault(id_c, []).append(pos)

        coppie_ordinate = sorted(punteggi_totali.items(), key=lambda x: x[1])
        classifica_finale = [id_c for id_c, _ in coppie_ordinate]
        return {pos: id_c for pos, id_c in enumerate(classifica_finale, 1)}, punteggi_totali
