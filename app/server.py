# On importe les outils Flask dont on a besoin
from flask import Flask, request, render_template, send_from_directory, redirect, session
import os  # pour créer des dossiers, lister des fichiers

# On importe nos fonctions de base de données (fichier database.py)
from database import verifier_connexion, creer_compte, lister_comptes, enregistrer_log, lister_logs

# Création de l'application Flask
app = Flask(__name__)

# Clé secrète pour chiffrer les sessions (cookies côté serveur)
app.secret_key = "dockshare_secret_2024"

# Dossier de stockage des fichiers uploadés
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # crée le dossier s'il n'existe pas

# ── Page de connexion ────────────────────────────────────────────────────────
@app.route("/", methods=["GET", "POST"])
def login():
    erreur = None  # pas d'erreur au départ

    if request.method == "POST":               # si le formulaire a été soumis
        nom = request.form["nom"]              # récupère le champ "nom" du formulaire
        mdp = request.form["mdp"]              # récupère le champ "mdp" du formulaire

        utilisateur = verifier_connexion(nom, mdp)  # interroge la base de données

        if utilisateur:                              # si un compte correspond
            session["utilisateur"] = utilisateur["nom"]   # retient le nom
            session["role"]        = utilisateur["role"]  # retient le rôle
            return redirect("/fichiers")                  # redirige vers l'app
        else:
            erreur = "Nom ou mot de passe incorrect."

    return render_template("login.html", erreur=erreur)

# ── Page principale : liste et upload de fichiers ────────────────────────────
@app.route("/fichiers")
def fichiers():
    # Protection : si pas connecté → retour au login
    if "utilisateur" not in session:
        return redirect("/")

    # Récupère les fichiers présents sur le disque
    fichiers_disque = os.listdir(UPLOAD_FOLDER)

    # Pour chaque fichier, cherche le dernier log d'upload correspondant
    import sqlite3 as _sqlite3
    conn = _sqlite3.connect('dockshare.db')
    conn.row_factory = _sqlite3.Row
    curseur = conn.cursor()

    fichiers = []
    for nom in fichiers_disque:
        curseur.execute(
            "SELECT utilisateur FROM logs WHERE fichier = ? AND action = 'upload' ORDER BY id DESC LIMIT 1",
            (nom,)
        )
        row = curseur.fetchone()
        fichiers.append({
            "nom": nom,
            "uploader": row["utilisateur"] if row else "inconnu"
        })
    conn.close()

    return render_template(
        "index.html",
        fichiers=fichiers,
        utilisateur=session["utilisateur"],
        role=session["role"]
    )

# ── Upload d'un fichier ──────────────────────────────────────────────────────
@app.route("/upload", methods=["POST"])
def upload():
    if "utilisateur" not in session:   # protection
        return redirect("/")

    fichier = request.files["fichier"]          # récupère le fichier du formulaire
    if fichier.filename != "":                  # vérifie qu'un fichier a été choisi
        chemin = os.path.join(UPLOAD_FOLDER, fichier.filename)
        fichier.save(chemin)                    # sauvegarde sur le disque
        enregistrer_log(session["utilisateur"], "upload", fichier.filename)

    return redirect("/fichiers")

# ── Téléchargement d'un fichier ──────────────────────────────────────────────
@app.route("/download/<nom>")
def download(nom):
    if "utilisateur" not in session:   # protection
        return redirect("/")
    # as_attachment=True force le téléchargement (plutôt que l'affichage)
    enregistrer_log(session["utilisateur"], "download", nom)
    return send_from_directory(UPLOAD_FOLDER, nom, as_attachment=True)

# ── Déconnexion ──────────────────────────────────────────────────────────────
@app.route("/logout")
def logout():
    session.clear()       # supprime toutes les données de session
    return redirect("/")  # retour à la page de login

# ── Page admin : créer et lister des comptes ─────────────────────────────────
@app.route("/admin", methods=["GET", "POST"])
def admin():
    # Seul un admin connecté peut accéder ici
    if session.get("role") != "admin":
        return redirect("/")

    message = None

    if request.method == "POST":
        nouveau_nom  = request.form["nom"]
        nouveau_mdp  = request.form["mdp"]
        nouveau_role = request.form["role"]

        succes = creer_compte(nouveau_nom, nouveau_mdp, nouveau_role)

        if succes:
            message = f"Compte '{nouveau_nom}' créé avec succès."
        else:
            message = f"Erreur : le nom '{nouveau_nom}' est déjà pris."

    comptes = lister_comptes()   # récupère tous les comptes pour les afficher
    logs    = lister_logs()      # récupère tous les logs d'activité
    return render_template("admin.html", message=message, comptes=comptes, logs=logs)

# ── Lancement du serveur ─────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
    # host="0.0.0.0" : écoute sur toutes les interfaces (obligatoire dans Docker)
    # port=5000       : port utilisé par le serveur
