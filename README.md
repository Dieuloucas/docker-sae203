# ShareBox — SAE 2.03

Serveur de partage de fichiers sécurisé, containerisé avec Docker.
Authentification par login/mot de passe, comptes stockés en SQLite.

## Lancer le projet en 3 commandes

```bash
git clone git@github.com:TON_USERNAME/sharebox.git
cd sharebox
docker build -t sharebox .
docker run -d -p 5000:5000 --name sharebox-app sharebox
```

Ouvrir http://localhost:5000  
Compte admin par défaut : `admin` / `admin123`
