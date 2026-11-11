# app.py
import streamlit as st
import pandas as pd
import os
import time
from database import init_db, esegui_query
from skating_engine import SkatingEngine, DISCIPLINE_PREDEFINITE
from reporter import VerbalReporter

st.set_page_config(page_title="Scrutineer Cloud Pro v3", layout="wide", page_icon="🌐")
init_db()

if "ruolo_corrente" in st.session_state and st.session_state.ruolo_corrente in ["🎙️ Presentatore / Speaker (Tablet)", "📊 Tabellone Pubblico / Scrutinio"]:
    time.sleep(5)
    st.rerun()

ruolo = st.sidebar.radio(
    "📱 Scegli Interfaccia Postazione:", 
    ["🎬 Direzione Gara (PC Centrale)", "⚖️ Pannello Giudici (Tablet)", "🎙️ Presentatore / Speaker (Tablet)", "📊 Tabellone Pubblico / Scrutinio"],
    key="ruolo_radio"
)
st.session_state.ruolo_corrente = ruolo

atleti_db = esegui_query("SELECT dorsale, nome, categoria FROM atleti")
anagrafica = {row[0]: row[1] for row in atleti_db}
categories_disponibili = list(set(row[2] for row in atleti_db)) if atleti_db else ["Nessuna"]

if ruolo == "🎬 Direzione Gara (PC Centrale)":
    st.header("🎬 Direzione Gara — Controllo Centralizzato e Sblocchi")
    
    col1, col2 = st.columns(2)
    with col1:
        cat_nome = st.text_input("Crea Categoria", placeholder="Es: Coppia Adulti Classe A")
        stile = st.selectbox("Seleziona Stile", list(DISCIPLINE_PREDEFINITE.keys()))
        balli = st.multiselect("Balli", DISCIPLINE_PREDEFINITE[stile], default=DISCIPLINE_PREDEFINITE[stile])
        
    with col2:
        ora_inizio = st.text_input("Orario Previsto Inizio (HH:MM)", "14:30")
        num_g = st.number_input("Numero Giudici a Pannello", min_value=3, max_value=11, value=5, step=2)
        st.session_state.num_giudici = num_g

    if st.button("📅 Pianifica ed Inserisci in Tabella Oraria"):
        for b in balli:
            esegui_query("INSERT INTO cronologico (orario, categoria, ballo, fase, stato) VALUES (?, ?, ?, 'Finale', 'In Programma')", (ora_inizio, cat_nome, b))
        st.success("Balli inseriti nel flusso temporale!")

    st.divider()
    st.subheader("🛡️ Sicurezza: Sblocco Voti Inviati dai Giudici")
    voti_inviati = esegui_query("SELECT DISTINCT ballo, giudice_idx FROM voti")
    if voti_inviati:
        for b, g_idx in voti_inviati:
            if st.button(f"🔓 Resetta e Sblocca Voti di Giudice {g_idx+1} per {b}", key=f"reset_{b}_{g_idx}"):
                esegui_query("DELETE FROM voti WHERE ballo = ? AND giudice_idx = ?", (b, g_idx))
                st.toast(f"Voti sbloccati per Giudice {g_idx+1}!")
                st.rerun()
    else:
        st.caption("Nessun voto inviato bloccato al momento.")

    st.divider()
    st.subheader("📥 Importazione Anagrafica Competitori")
    upload_file = st.file_uploader("Carica File Excel/CSV Atleti", type=["csv", "xlsx"])
    if upload_file and cat_nome:
        df = pd.read_csv(upload_file) if upload_file.name.endswith('.csv') else pd.read_excel(upload_file)
        for _, row in df.iterrows():
            esegui_query("INSERT OR REPLACE INTO atleti (dorsale, nome, categoria) VALUES (?, ?, ?)", (int(row['Dorsale']), str(row['Nome']), cat_nome))
        st.success(f"Caricate {len(df)} unità per la categoria {cat_nome}!")

elif ruolo == "⚖️ Pannello Giudici (Tablet)":
    st.header("📲 Interfaccia Giudice di Gara")
    num_g = st.session_state.get("num_giudici", 5)
    g_id = st.selectbox("Seleziona la tua Postazione Giudice:", [i for i in range(1, int(num_g) + 1)])
    g_idx = g_id - 1
    
    attivi = esegui_query("SELECT id, categoria, ballo FROM cronologico WHERE stato = 'In Corso'")
    if not attivi:
        st.warning("⏳ In attesa che il Direttore o lo Speaker avviino il prossimo ballo...")
    else:
        ev_id, cat, ballo = attivi[0][0], attivi[0][1], attivi[0][2]
        st.subheader(f"Valutazione Corrente: {cat} — Ballo: **{ballo}**")
        
        gia_inviato = esegui_query("SELECT COUNT(*) FROM voti WHERE ballo = ? AND giudice_idx = ?", (ballo, g_idx))[0][0]
        atleti_cat = esegui_query("SELECT dorsale, nome FROM atleti WHERE categoria = ?", (cat,))
        
        if gia_inviato > 0:
            st.success("✅ I tuoi voti per questo ballo sono stati inviati e sigillati con successo.")
            for d, nome in atleti_cat:
                voto_salvato = esegui_query("SELECT valore FROM voti WHERE ballo = ? AND giudice_idx = ? AND dorsale = ?", (ballo, g_idx, d))
                v_stampa = voto_salvato[0][0] if voto_salvato else "-"
                st.markdown(f"**Dorsale {d}**: Posizione assegnata -> **{v_stampa}°**")
        else:
            voti_temporanei = {}
            for d, nome in atleti_cat:
                voti_temporanei[d] = st.number_input(f"Posizione per Dorsale {d} ({nome})", min_value=1, max_value=len(atleti_cat), value=1, key=f"jud_{g_idx}_{d}")
            
            if st.button("🔒 INVIA E BLOCCA SCHEDA VOTI", type="primary", use_container_width=True):
                for d, v in voti_temporanei.items():
                    esegui_query("INSERT INTO voti (fase, ballo, giudice_idx, dorsale, valore) VALUES ('Finale', ?, ?, ?, ?)", (ballo, g_idx, d, v))
                st.success("Voti salvati definitivamente!")
                st.rerun()

elif ruolo == "🎙️ Presentatore / Speaker (Tablet)":
    st.header("🎙️ Regia di Gara & Ordine di Discesa in Pista")
    st.caption("🔄 Pagina in aggiornamento automatico continuo.")
    
    st.subheader("📅 Cronologico Orario delle Categorie")
    crono_data = esegui_query("SELECT orario, categoria, ballo, stato, id FROM cronologico ORDER BY id ASC")
    
    for ora, cat, ballo, stato, cid in crono_data:
        col_c1, col_c2, col_c3 = st.columns(3)
        col_c1.markdown(f"**⏰ Orario Teorico: {ora}**")
        col_c2.markdown(f"🏆 **{cat}** <br> 🕺 Ballo: *{ballo}*", unsafe_allow_html=True)
        
        if stato == "In Programma":
            if col_c3.button("▶️ Metti in Pista", key=f"start_{cid}"):
                esegui_query("UPDATE cronologico SET stato = 'In Corso' WHERE id = ?", (cid,))
                st.rerun()
        elif stato == "In Corso":
            col_c3.markdown("🔴 **IN PISTA ADESSO**")
            if col_c3.button("⏹️ Concludi ed Archivia", key=f"stop_{cid}"):
                esegui_query("UPDATE cronologico SET stato = 'Terminato' WHERE id = ?", (cid,))
                st.rerun()
        else:
            col_c3.write("✅ Concluso")
            
    attivi = esegui_query("SELECT categoria, ballo FROM cronologico WHERE stato = 'In Corso'")
    if attivi:
        st.divider()
        st.subheader(f"📣 ATLETI DA CHIAMARE IN PISTA IN QUESTO MOMENTO:")
        atleti_in_pista = esegui_query("SELECT dorsale, nome FROM atleti WHERE categoria = ?", (attivi[0][0],))
        for d, n in atleti_in_pista:
            st.markdown(f"🎯 **Dorsale {d}** — {n}")

elif ruolo == "📊 Tabellone Pubblico / Scrutinio":
    st.header("📊 Scrutinio in Tempo Reale & Classifiche Finali")
    cat_scelta = st.selectbox("Seleziona la Categoria da Scrutinare", categories_disponibili)
    
    if cat_scelta != "Nessuna":
        balli_cat = esegui_query("SELECT DISTINCT ballo FROM cronologico WHERE categoria = ?", (cat_scelta,))
        balli_lista = [b[0] for b in balli_cat]
        
        st.subheader("📬 Monitoraggio schede giudici pervenute:")
        num_g = st.session_state.get("num_giudici", 5)
        
        for b in balli_lista:
            voti_ricevuti = esegui_query("SELECT COUNT(DISTINCT giudice_idx) FROM voti WHERE ballo = ?", (b,))[0][0]
            if voti_ricevuti >= int(num_g):
                st.success(f"🟢 Ballo {b}: Schede Giudici Complete ({voti_ricevuti}/{num_g})")
            else:
                st.warning(f"🟡 Ballo {b}: Ricevute schede da {voti_ricevuti} giudici su {num_g} totali")
                
        if st.button("🧮 Esegui Calcolo Skating System", type="primary"):
            engine = SkatingEngine(num_giudici=int(num_g))
            risultati_balli = {}
            atleti_cat = esegui_query("SELECT dorsale FROM atleti WHERE categoria = ?", (cat_scelta,))
            id_atleti = [a[0] for a in atleti_cat]
            
            for ballo in balli_lista:
                voti_ballo = {}
                for id_c in id_atleti:
                    voti_db = esegui_query("SELECT valore FROM voti WHERE ballo = ? AND dorsale = ?", (ballo, id_c))
                    voti_ballo[id_c] = [v[0] for v in voti_db] if voti_db else [1]*int(num_g)
                risultati_balli[ballo] = engine.calcola_singolo_ballo(voti_ballo)
                
            classifica_finale, punteggi_totali = engine.calcola_combinata(risultati_balli)
            
            st.subheader("🥇 CLASSIFICA UFFICIALE")
            for pos, id_c in classifica_finale.items():
                st.write(f"🏆 **{pos}° Posto**: Dorsale **{id_c}** — {anagrafica.get(id_c, f'Atleta {id_c}')} (Totale Somma Piazzamenti: {punteggi_totali[id_c]})")
                
            os.makedirs("generated", exist_ok=True)
            pdf_path = VerbalReporter.genera_pdf_completo("Gran Premio Danza Sportiva", cat_scelta, balli_lista, classifica_finale, punteggi_totali, anagrafica)
            with open(pdf_path, "rb") as f:
                st.download_button("📥 Scarica Verbale Ufficiale Convalidato (PDF)", data=f, file_name=f"verbale_{cat_scelta.replace(' ', '_')}.pdf")
