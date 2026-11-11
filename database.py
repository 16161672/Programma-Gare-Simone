# database.py
import sqlite3

def init_db():
    conn = sqlite3.connect("gara.db")
    cursor = conn.cursor()
    
    # Tabella Atleti
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS atleti (
            dorsale INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            categoria TEXT NOT NULL
        )
    """)
    
    # Tabella Voti (Crocette e Piazzamenti)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS voti (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fase TEXT NOT NULL, -- 'Eliminatoria' o 'Finale'
            ballo TEXT NOT NULL,
            giudice_idx INTEGER NOT NULL,
            dorsale INTEGER NOT NULL,
            valore INTEGER NOT NULL -- 1 per Crocetta, numero posizione per Piazzamento
        )
    """)
    
    # Tabella Cronologico / Time-Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cronologico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            orario TEXT NOT NULL,
            categoria TEXT NOT NULL,
            ballo TEXT NOT NULL,
            fase TEXT NOT NULL,
            stato TEXT DEFAULT 'In Programma' -- 'In Programma', 'In Corso', 'Terminato'
        )
    """)
    
    conn.commit()
    conn.close()

def esegui_query(query, params=()):
    conn = sqlite3.connect("gara.db")
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    data = cursor.fetchall()
    conn.close()
    return data
