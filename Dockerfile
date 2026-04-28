# Étape 1 : image de base — Linux Debian vierge, comme dans les TPs
FROM debian:latest

# Étape 2 : installer Python et pip
# && enchaîne sur une seule couche, \ continue la ligne, rm -rf allège l'image
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Étape 3 : définir /app comme dossier de travail dans le conteneur
WORKDIR /app

# Étape 4 : copier le code source (dossier app/ de l'hôte → /app du conteneur)
COPY app/ .
# requirements.txt est à la racine du dépôt, on le copie séparément
COPY requirements.txt .

# Étape 5 : installer Flask (--break-system-packages requis sur Debian 12+)
RUN pip3 install --break-system-packages -r requirements.txt

# Étape 6 : initialiser la base de données pendant le build
RUN python3 init_db.py

# Étape 7 : documenter le port utilisé (nécessaire pour -p dans docker run)
EXPOSE 5000

# Étape 8 : commande lancée automatiquement au démarrage du conteneur
CMD ["python3", "server.py"]
