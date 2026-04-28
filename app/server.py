# On importe les outils Flask dont on a besoin
from flask import Flask, request, render_template, send_from_directory, redirect, session
import os  # pour créer des dossiers, lister des fichiers

# On importe nos fonctions de base de données (fichier database.py)
from database import verifier_connexion, creer_compte, lister_comptes

# Création de l'application Flask
app = Flask(__name__)

# Clé secrète pour chiffrer les sessions (cookies côté serveur)
app.secret_key = "sharebox_secret_2024"

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

    liste = os.listdir(UPLOAD_FOLDER)   # liste tous les fichiers du dossier uploads
    return render_template(
        "index.html",
        fichiers=liste,
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

    return redirect("/fichiers")

# ── Téléchargement d'un fichier ──────────────────────────────────────────────
@app.route("/download/<nom>")
def download(nom):
    if "utilisateur" not in session:   # protection
        return redirect("/")
    # as_attachment=True force le téléchargement (plutôt que l'affichage)
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
    return render_template("admin.html", message=message, comptes=comptes)

# ── Lancement du serveur ─────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
    # host="0.0.0.0" : écoute sur toutes les interfaces (obligatoire dans Docker)
    # port=5000       : port utilisé par le serveur
