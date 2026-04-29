import sqlite3

conn = sqlite3.connect("dockshare.db")
curseur = conn.cursor()

# Crée la table si elle n'existe pas déjà
# INTEGER PRIMARY KEY AUTOINCREMENT : l'id s'incrémente automatiquement
# UNIQUE : deux utilisateurs ne peuvent pas avoir le même nom
curseur.execute("""
    CREATE TABLE IF NOT EXISTS utilisateurs (
        id   INTEGER PRIMARY KEY AUTOINCREMENT,
        nom  TEXT NOT NULL UNIQUE,
        mdp  TEXT NOT NULL,
        role TEXT NOT NULL
    )
""")

# Insère les comptes par défaut
# INSERT OR IGNORE : ne plante pas si le compte existe déjà
curseur.execute(
    "INSERT OR IGNORE INTO utilisateurs (nom, mdp, role) VALUES (?, ?, ?)",
    ("admin", "admin123", "admin")
)
curseur.execute(
    "INSERT OR IGNORE INTO utilisateurs (nom, mdp, role) VALUES (?, ?, ?)",
    ("alice", "alice123", "user")
)

curseur.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        utilisateur TEXT NOT NULL,
        action      TEXT NOT NULL,
        fichier     TEXT NOT NULL,
        date        TEXT NOT NULL
    )
""")

conn.commit()  # valide les insertions
conn.close()

print("Base de données initialisée avec succès.")
print("Comptes créés : admin / alice")
