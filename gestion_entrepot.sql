CREATE DATABASE gestion_entrepot;

USE gestion_entrepot;

-- Table des produits
CREATE TABLE produits (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(255) NOT NULL,
    quantite INT NOT NULL
);

-- Table des clients
CREATE TABLE clients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(255) NOT NULL,
    adresse VARCHAR(255) NOT NULL
);

-- Table des commandes (avec date de commande)
CREATE TABLE commandes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    client_id INT NOT NULL,
    produit VARCHAR(255) NOT NULL,
    quantite INT NOT NULL,
    date_commande DATETIME NOT NULL,  -- Ajout de la colonne date_commande
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
);
    
