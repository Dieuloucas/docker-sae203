import sqlite3
from datetime import datetime

DB_PATH = "dockshare.db"

def get_connection():
    """Ouvre et retourne une connexion à la base de données."""
    conn = sqlite3.connect(DB_PATH)
    # row_factory permet d'accéder aux colonnes par leur nom (ex: row["nom"])
    # plutôt que par index (ex: row[0])
    conn.row_factory = sqlite3.Row
    return conn

def verifier_connexion(nom, mdp):
    """
    Vérifie si le nom + mot de passe correspondent à un compte.
    Retourne la ligne (id, nom, mdp, role) si OK, sinon None.
    """
    conn = get_connection()
    # cursor() permet d'exécuter des requêtes SQL
    curseur = conn.cursor()
    # Le ? est un paramètre sécurisé — évite les injections SQL
    curseur.execute(
        "SELECT * FROM utilisateurs WHERE nom = ? AND mdp = ?",
        (nom, mdp)
    )
    utilisateur = curseur.fetchone()  # récupère la première ligne trouvée (ou None)
    conn.close()                      # toujours fermer la connexion après utilisation
    return utilisateur

def creer_compte(nom, mdp, role):
    """
    Crée un nouveau compte dans la base de données.
    Retourne True si OK, False si le nom est déjà pris.
    """
    conn = get_connection()
    curseur = conn.cursor()
    try:
        curseur.execute(
            "INSERT INTO utilisateurs (nom, mdp, role) VALUES (?, ?, ?)",
            (nom, mdp, role)
        )
        conn.commit()  # valide les changements dans la base de données
        conn.close()
        return True
    except sqlite3.IntegrityError:
        # IntegrityError est levée si le nom est déjà pris (contrainte UNIQUE)
        conn.close()
        return False

def lister_comptes():
    """Retourne la liste de tous les comptes (sans les mots de passe)."""
    conn = get_connection()
    curseur = conn.cursor()
    curseur.execute("SELECT id, nom, role FROM utilisateurs")
    comptes = curseur.fetchall()  # récupère TOUTES les lignes
    conn.close()
    return comptes

def enregistrer_log(utilisateur, action, fichier):
    """Enregistre une action (upload ou download) dans la table logs."""
    conn = get_connection()
    curseur = conn.cursor()
    # datetime.now() retourne la date et heure actuelles
    # strftime formate la date en texte lisible : "2024-04-28 14:35:22"
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    curseur.execute(
        "INSERT INTO logs (utilisateur, action, fichier, date) VALUES (?, ?, ?, ?)",
        (utilisateur, action, fichier, date)
    )
    conn.commit()
    conn.close()

def lister_logs():
    """Retourne tous les logs, du plus récent au plus ancien."""
    conn = get_connection()
    curseur = conn.cursor()
    # ORDER BY id DESC : le plus récent en premier
    curseur.execute("SELECT * FROM logs ORDER BY id DESC")
    logs = curseur.fetchall()
    conn.close()
    return logs
