README : 

Pour se connecter a la database sql :
sudo systemctl start mysql # lancer le serveur sql
sudo systemctl status mysql # Voire l'état du serveur
mysql -u root -p 
USE gestion_stock;
Si la database est deja créer 
Sinon:
CREATE DATABASE gestion_stock;
USE gestion_stock;

CREATE TABLE produits (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(255) NOT NULL,
    quantite INT NOT NULL
);

CREATE TABLE clients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(255) NOT NULL,
    adresse VARCHAR(255) NOT NULL,
    commande VARCHAR(255) NOT NULL,
    quantite INT NOT NULL
);

NE PAS OUBLIER LE MDP DANS LE CODE PYTHON


SI JAMAIS BUG :

sudo apt install python3-venv
python3 -m venv myenv
source myenv/bin/activate
pip install mysql-connector-python
python prod.py
