import mysql.connector
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import os
import pickle

class Database:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",  # Remplacez par votre nom d'utilisateur MySQL
            password="azerty123",  # Remplacez par votre mot de passe MySQL
            database="gestion_entrepot"
        )
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS produits (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nom VARCHAR(255) NOT NULL,
                    quantite INT NOT NULL
                )
            """)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS clients (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nom VARCHAR(255) NOT NULL,
                    adresse VARCHAR(255) NOT NULL
                )
            """)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS commandes (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    client_id INT NOT NULL,
                    produit VARCHAR(255) NOT NULL,
                    quantite INT NOT NULL,
                    date_commande DATETIME NOT NULL,
                    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
                )
            """)
            self.conn.commit()
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue lors de la création des tables : {str(e)}")
            self.conn.rollback()

    def ajouter_produit(self, nom, quantite):
        sql = "INSERT INTO produits (nom, quantite) VALUES (%s, %s)"
        self.cursor.execute(sql, (nom, quantite))
        self.conn.commit()

    def afficher_produits(self):
        self.cursor.execute("SELECT * FROM produits")
        return self.cursor.fetchall()

    def ajouter_client(self, nom, adresse):
        sql = "INSERT INTO clients (nom, adresse) VALUES (%s, %s)"
        self.cursor.execute(sql, (nom, adresse))
        self.conn.commit()

    def afficher_clients(self):
        self.cursor.execute("SELECT * FROM clients")
        return self.cursor.fetchall()

    def supprimer_client(self, client_id):
        try:
            sql = "DELETE FROM clients WHERE id = %s"
            self.cursor.execute(sql, (client_id,))
            self.conn.commit()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la suppression du client : {str(e)}")

    def supprimer_produit(self, produit_id):
        try:
            sql = "DELETE FROM produits WHERE id = %s"
            self.cursor.execute(sql, (produit_id,))
            self.conn.commit()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la suppression du produit : {str(e)}")

    def supprimer_commande(self, commande_id):
        try:
            sql = "DELETE FROM commandes WHERE id = %s"
            self.cursor.execute(sql, (commande_id,))
            self.conn.commit()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la suppression de la commande : {str(e)}")

    def restaurer(self):
        try:
            self.cursor.execute("DROP TABLE IF EXISTS commandes")
            self.cursor.execute("DROP TABLE IF EXISTS clients")
            self.cursor.execute("DROP TABLE IF EXISTS produits")
            messagebox.showinfo("Restaurer", "Tables supprimées avec succès.")
            self.create_table()
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue lors de la restauration : {str(e)}")
        self.conn.commit()

    def ajouter_commande(self, client_id, produit, quantite):
        try:
            # Vérification si le client existe
            self.cursor.execute("SELECT id FROM clients WHERE id = %s", (client_id,))
            client_exists = self.cursor.fetchall()

            if not client_exists:
                return False  # Client n'existe pas

            stock_quantite = self.get_quantite_produit(produit)
            if stock_quantite >= quantite:
                date_commande = datetime.now()
                sql = "INSERT INTO commandes (client_id, produit, quantite, date_commande) VALUES (%s, %s, %s, %s)"
                self.cursor.execute(sql, (client_id, produit, quantite, date_commande))
                self.decrease_product_stock(produit, quantite)
                self.conn.commit()
                return True
            else:
                return False  # Pas assez de stock
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'ajout de la commande : {str(e)}")
            self.conn.rollback()

    def decrease_product_stock(self, produit, quantite):
        sql = "UPDATE produits SET quantite = quantite - %s WHERE nom = %s"
        self.cursor.execute(sql, (quantite, produit))
        self.conn.commit()

    def afficher_commandes(self):
        self.cursor.execute("SELECT * FROM commandes")
        return self.cursor.fetchall()

    def get_quantite_produit(self, nom_produit):
        self.cursor.execute("SELECT quantite FROM produits WHERE nom = %s", (nom_produit,))
        result = self.cursor.fetchone()
        return result[0] if result else 0

    def get_client_nom(self, client_id):
        self.cursor.execute("SELECT nom FROM clients WHERE id = %s", (client_id,))
        result = self.cursor.fetchone()
        return result[0] if result else "Inconnu"

    def close(self):
        self.cursor.close()
        self.conn.close()

    def sauvegarder_donnees(self):
        try:
            with open("backup.pkl", "wb") as f:
                # Sauvegarde des données des produits
                self.cursor.execute("SELECT * FROM produits")
                produits = self.cursor.fetchall()

                # Sauvegarde des données des clients
                self.cursor.execute("SELECT * FROM clients")
                clients = self.cursor.fetchall()

                # Sauvegarde des données des commandes
                self.cursor.execute("SELECT * FROM commandes")
                commandes = self.cursor.fetchall()

                # Sauvegarde dans le fichier
                pickle.dump({"produits": produits, "clients": clients, "commandes": commandes}, f)
                messagebox.showinfo("Sauvegarde", "Les données ont été sauvegardées avec succès.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde : {str(e)}")

    def restaurer_donnees(self):
        if os.path.exists("backup.pkl"):
            with open("backup.pkl", "rb") as f:
                data = pickle.load(f)
                self.restaurer()
                # Restauration des données
                for produit in data["produits"]:
                    self.ajouter_produit(produit[1], produit[2])  # produit[1] = nom, produit[2] = quantite
                for client in data["clients"]:
                    self.ajouter_client(client[1], client[2])  # client[1] = nom, client[2] = adresse
                for commande in data["commandes"]:
                    self.ajouter_commande(commande[1], commande[2], commande[3])  # commande[1] = client_id, commande[2] = produit, commande[3] = quantite
                messagebox.showinfo("Restauration", "Les données ont été restaurées avec succès.")
        else:
            messagebox.showerror("Erreur", "Aucune sauvegarde trouvée.")

class App:
    def __init__(self, root, db):
        self.root = root
        self.root.title("Gestion d'Entrepôt")
        self.root.geometry("800x600")
        
        self.db = db

        # Création d'un Notebook pour les onglets
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True)

        # Onglet Produits
        self.tab_produits = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_produits, text="Produits")

        # Onglet Clients
        self.tab_clients = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_clients, text="Clients")

        # Onglet Commandes
        self.tab_commandes = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_commandes, text="Commandes")

        # Onglet Sauvegarder/Restauration
        self.tab_restaurer = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_restaurer, text="Sauvegarder/Restauration")

        # Widgets pour l'onglet Produits
        self.create_product_widgets()

        # Widgets pour l'onglet Clients
        self.create_client_widgets()

        # Widgets pour l'onglet Commandes
        self.create_order_widgets()

        # Widgets pour l'onglet Sauvegarde/Restauration
        self.create_restore_widgets()

    def create_product_widgets(self):
        # Label et champs d'entrée pour ajouter un produit
        self.lbl_nom_produit = ttk.Label(self.tab_produits, text="Nom du produit:")
        self.lbl_nom_produit.pack()
        self.entree_nom_produit = ttk.Entry(self.tab_produits)
        self.entree_nom_produit.pack()

        self.lbl_quantite_produit = ttk.Label(self.tab_produits, text="Quantité:")
        self.lbl_quantite_produit.pack()
        self.entree_quantite_produit = ttk.Entry(self.tab_produits)
        self.entree_quantite_produit.pack()

        self.btn_ajouter_produit = ttk.Button(self.tab_produits, text="Ajouter Produit", command=self.ajouter_produit)
        self.btn_ajouter_produit.pack()

        self.tree_produits = ttk.Treeview(self.tab_produits, columns=("ID", "Nom", "Quantité"), show="headings")
        self.tree_produits.heading("ID", text="ID")
        self.tree_produits.heading("Nom", text="Nom")
        self.tree_produits.heading("Quantité", text="Quantité")
        self.tree_produits.pack(fill='both', expand=True)

        self.charger_produits()

    def create_client_widgets(self):
        # Label et champs d'entrée pour ajouter un client
        self.lbl_nom_client = ttk.Label(self.tab_clients, text="Nom du client:")
        self.lbl_nom_client.pack()
        self.entree_nom_client = ttk.Entry(self.tab_clients)
        self.entree_nom_client.pack()

        self.lbl_adresse_client = ttk.Label(self.tab_clients, text="Adresse:")
        self.lbl_adresse_client.pack()
        self.entree_adresse_client = ttk.Entry(self.tab_clients)
        self.entree_adresse_client.pack()

        self.btn_ajouter_client = ttk.Button(self.tab_clients, text="Ajouter Client", command=self.ajouter_client)
        self.btn_ajouter_client.pack()

        self.tree_clients = ttk.Treeview(self.tab_clients, columns=("ID", "Nom", "Adresse"), show="headings")
        self.tree_clients.heading("ID", text="ID")
        self.tree_clients.heading("Nom", text="Nom")
        self.tree_clients.heading("Adresse", text="Adresse")
        self.tree_clients.pack(fill='both', expand=True)

        self.charger_clients()

    def create_order_widgets(self):
        # Label et champs d'entrée pour ajouter une commande
        self.lbl_client_id = ttk.Label(self.tab_commandes, text="ID Client:")
        self.lbl_client_id.pack()
        self.entree_client_id = ttk.Entry(self.tab_commandes)
        self.entree_client_id.pack()

        self.lbl_nom_produit_cmd = ttk.Label(self.tab_commandes, text="Nom du produit:")
        self.lbl_nom_produit_cmd.pack()
        self.entree_nom_produit_cmd = ttk.Entry(self.tab_commandes)
        self.entree_nom_produit_cmd.pack()

        self.lbl_quantite_cmd = ttk.Label(self.tab_commandes, text="Quantité:")
        self.lbl_quantite_cmd.pack()
        self.entree_quantite_cmd = ttk.Entry(self.tab_commandes)
        self.entree_quantite_cmd.pack()

        self.btn_ajouter_commande = ttk.Button(self.tab_commandes, text="Ajouter Commande", command=self.ajouter_commande)
        self.btn_ajouter_commande.pack()

        self.tree_commandes = ttk.Treeview(self.tab_commandes, columns=("ID", "Client ID", "Produit", "Quantité", "Date"), show="headings")
        self.tree_commandes.heading("ID", text="ID")
        self.tree_commandes.heading("Client ID", text="Client ID")
        self.tree_commandes.heading("Produit", text="Produit")
        self.tree_commandes.heading("Quantité", text="Quantité")
        self.tree_commandes.heading("Date", text="Date")
        self.tree_commandes.pack(fill='both', expand=True)

        self.charger_commandes()

    def create_restore_widgets(self):
        self.btn_sauvegarder = ttk.Button(self.tab_restaurer, text="Sauvegarder Données", command=self.db.sauvegarder_donnees)
        self.btn_sauvegarder.pack()

        self.btn_restaurer = ttk.Button(self.tab_restaurer, text="Restaurer Données", command=self.db.restaurer_donnees)
        self.btn_restaurer.pack()

    def ajouter_produit(self):
        nom = self.entree_nom_produit.get()
        quantite = self.entree_quantite_produit.get()

        if not nom or not quantite.isdigit() or int(quantite) < 0:
            messagebox.showerror("Erreur", "Veuillez entrer un nom valide et une quantité valide (nombre positif).")
            return

        self.db.ajouter_produit(nom, int(quantite))
        self.charger_produits()
        self.entree_nom_produit.delete(0, tk.END)
        self.entree_quantite_produit.delete(0, tk.END)

    def charger_produits(self):
        for row in self.tree_produits.get_children():
            self.tree_produits.delete(row)
        for produit in self.db.afficher_produits():
            self.tree_produits.insert("", tk.END, values=produit)

    def ajouter_client(self):
        nom = self.entree_nom_client.get()
        adresse = self.entree_adresse_client.get()

        if not nom or not adresse:
            messagebox.showerror("Erreur", "Veuillez entrer un nom et une adresse valides.")
            return

        self.db.ajouter_client(nom, adresse)
        self.charger_clients()
        self.entree_nom_client.delete(0, tk.END)
        self.entree_adresse_client.delete(0, tk.END)

    def charger_clients(self):
        for row in self.tree_clients.get_children():
            self.tree_clients.delete(row)
        for client in self.db.afficher_clients():
            self.tree_clients.insert("", tk.END, values=client)

    def ajouter_commande(self):
        client_id = self.entree_client_id.get()
        produit = self.entree_nom_produit_cmd.get()
        quantite = self.entree_quantite_cmd.get()

        if not client_id.isdigit() or not produit or not quantite.isdigit() or int(quantite) < 0:
            messagebox.showerror("Erreur", "Veuillez entrer un ID client valide, un produit et une quantité valide (nombre positif).")
            return

        success = self.db.ajouter_commande(int(client_id), produit, int(quantite))
        if success:
            messagebox.showinfo("Commande", "Commande ajoutée avec succès.")
            self.charger_commandes()
        else:
            messagebox.showerror("Erreur", "Erreur lors de l'ajout de la commande. Vérifiez si le produit est en stock ou si le client existe.")

        self.entree_client_id.delete(0, tk.END)
        self.entree_nom_produit_cmd.delete(0, tk.END)
        self.entree_quantite_cmd.delete(0, tk.END)

    def charger_commandes(self):
        for row in self.tree_commandes.get_children():
            self.tree_commandes.delete(row)
        for commande in self.db.afficher_commandes():
            self.tree_commandes.insert("", tk.END, values=commande)

def main():
    root = tk.Tk()
    db = Database()
    app = App(root, db)
    root.protocol("WM_DELETE_WINDOW", db.close)  # Fermer la connexion à la base de données lors de la fermeture de l'application
    root.mainloop()

if __name__ == "__main__":
    main()
