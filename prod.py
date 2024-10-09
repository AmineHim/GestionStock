import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import mysql.connector

class Database:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="azerty123",
            database="gestion_entrepot"
        )
        self.cursor = self.conn.cursor()

    def ajouter_produit(self, nom, quantite):
        sql = "INSERT INTO produits (nom, quantite) VALUES (%s, %s)"
        self.cursor.execute(sql, (nom, quantite))
        self.conn.commit()

    def afficher_produits(self):
        self.cursor.execute("SELECT * FROM produits")
        return self.cursor.fetchall()

    def rechercher_produit(self, keyword):
        sql = "SELECT * FROM produits WHERE nom LIKE %s"
        self.cursor.execute(sql, ('%' + keyword + '%',))
        return self.cursor.fetchall()

    def supprimer_produit(self, produit_id):
        sql = "DELETE FROM produits WHERE id = %s"
        self.cursor.execute(sql, (produit_id,))
        self.conn.commit()

    def mettre_a_jour_quantite_produit(self, produit, quantite):
        sql = "UPDATE produits SET quantite = quantite - %s WHERE nom = %s"
        self.cursor.execute(sql, (quantite, produit))
        self.conn.commit()

    def ajouter_client(self, nom, adresse):
        sql = "INSERT INTO clients (nom, adresse) VALUES (%s, %s)"
        self.cursor.execute(sql, (nom, adresse))
        self.conn.commit()

    def afficher_clients(self):
        self.cursor.execute("SELECT * FROM clients")
        return self.cursor.fetchall()

    def rechercher_client(self, keyword):
        sql = "SELECT * FROM clients WHERE nom LIKE %s"
        self.cursor.execute(sql, ('%' + keyword + '%',))
        return self.cursor.fetchall()

    def supprimer_client(self, client_id):
        sql = "DELETE FROM clients WHERE id = %s"
        self.cursor.execute(sql, (client_id,))
        self.conn.commit()

    def ajouter_commande(self, client_id, produit, quantite, date_commande):
        sql = "INSERT INTO commandes (client_id, produit, quantite, date_commande) VALUES (%s, %s, %s, %s)"
        try:
            self.cursor.execute(sql, (client_id, produit, quantite, date_commande))
            self.conn.commit()
            self.mettre_a_jour_quantite_produit(produit, quantite)  # Mise à jour du stock
            return True
        except mysql.connector.Error as e:
            print(e)
            return False

    def afficher_commandes(self):
        self.cursor.execute("SELECT * FROM commandes")
        return self.cursor.fetchall()

    def rechercher_commande(self, keyword):
        sql = "SELECT * FROM commandes WHERE produit LIKE %s"
        self.cursor.execute(sql, ('%' + keyword + '%',))
        return self.cursor.fetchall()

    def supprimer_commande(self, commande_id):
        sql = "DELETE FROM commandes WHERE id = %s"
        self.cursor.execute(sql, (commande_id,))
        self.conn.commit()

    def restaurer(self):
        self.cursor.execute("DROP TABLE IF EXISTS commandes")
        self.cursor.execute("DROP TABLE IF EXISTS clients")
        self.cursor.execute("DROP TABLE IF EXISTS produits")
        self.cursor.execute("""
            CREATE TABLE produits (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nom VARCHAR(255) NOT NULL,
                quantite INT NOT NULL
            )
        """)
        self.cursor.execute("""
            CREATE TABLE clients (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nom VARCHAR(255) NOT NULL,
                adresse VARCHAR(255) NOT NULL
            )
        """)
        self.cursor.execute("""
            CREATE TABLE commandes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                client_id INT NOT NULL,
                produit VARCHAR(255) NOT NULL,
                quantite INT NOT NULL,
                date_commande DATETIME NOT NULL,
                FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
            )
        """)
        self.conn.commit()

class App:
    def __init__(self, root, db):
        self.root = root
        self.db = db
        self.root.title("Gestion d'Entrepôt")
        self.root.geometry("1920x1080")

        # Création des onglets
        self.tab_control = ttk.Notebook(self.root)
        self.tab_produits = ttk.Frame(self.tab_control)
        self.tab_clients = ttk.Frame(self.tab_control)
        self.tab_commandes = ttk.Frame(self.tab_control)
        self.tab_restaurer = ttk.Frame(self.tab_control)

        self.tab_control.add(self.tab_produits, text="Produits")
        self.tab_control.add(self.tab_clients, text="Clients")
        self.tab_control.add(self.tab_commandes, text="Commandes")
        self.tab_control.add(self.tab_restaurer, text="Restaurer")
        self.tab_control.pack()

        self.create_product_widgets()
        self.create_client_widgets()
        self.create_order_widgets()
        self.create_restore_widgets()
        
        self.popup_shown = False
        self.show_info_popup()

    def show_info_popup(self):
         # Création du popup
        popup = tk.Toplevel(self.root)
        popup.title("Bienvenue dans Mon Application")
        popup.geometry("600x500")
        popup.config(bg="#f0f0f0")  # Couleur de fond

        popup.attributes('-topmost', True)
        
        # Message d'information
        message = (
            "Bienvenue dans notre application !\n\n"
            "Cette application vous permet de gérer vos produits et clients.\n"
            "Voici un aperçu des onglets disponibles :\n\n"
            "1. Produits : Ajoutez, supprimez et affichez vos produits.\n"
            "2. Clients : Ajoutez, supprimez et affichez vos clients.\n"
            "3. Commandes : Passez des commandes, affichez les détails des commandes, et supprimez celles qui ne sont plus nécessaires.\n"
            "4. Restaurer : Réinitialisez la base de données à zéro, ce qui supprimera toutes les données actuelles et vous permettra de repartir sur une base vierge.\n\n"
            "Utilisez les boutons pour naviguer facilement dans l'application.")

        label = tk.Label(popup, text=message, wraplength=300, justify="center", bg="#f0f0f0", font=("Helvetica", 12))
        label.pack(pady=20)

        # Bouton pour fermer le popup
        tk.Button(popup, text="Fermer", command=popup.destroy, bg="blue", fg="white", font=("Helvetica", 12)).pack(pady=10)

            
    def create_product_widgets(self):
        frame_produit = ttk.Frame(self.tab_produits)
        frame_produit.pack(pady=10, padx=10)

        # Champs de texte pour nom et quantité
        tk.Label(frame_produit, text="Nom du produit", font=("Helvetica", 12)).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.nom_produit_entry = tk.Entry(frame_produit, font=("Helvetica", 12), width=30)
        self.nom_produit_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame_produit, text="Quantité", font=("Helvetica", 12)).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.quantite_produit_entry = tk.Entry(frame_produit, font=("Helvetica", 12), width=30)
        self.quantite_produit_entry.grid(row=1, column=1, padx=5, pady=5)

        # Ajout d'un frame pour organiser les boutons
        frame_boutons = ttk.Frame(frame_produit)
        frame_boutons.grid(row=2, column=0, columnspan=2, pady=10)  # Placer ce frame sur la même grille, en dessous des champs

        # Boutons avec des positions différentes
        tk.Button(frame_boutons, text="Ajouter Produit", command=self.ajouter_produit, bg="gray", fg="white", font=("Helvetica", 12)).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_boutons, text="Clear", command=self.clear_entries, bg="gray", fg="white", font=("Helvetica", 12)).pack(side=tk.RIGHT, padx=5)
        tk.Button(frame_boutons, text="Afficher Produits", command=self.afficher_produits, bg="gray", fg="white", font=("Helvetica", 12)).pack(side=tk.LEFT, padx=5)

        # Autres boutons sous forme de lignes
        tk.Button(frame_produit, text="Rechercher Produit", command=self.rechercher_produit, bg="gray", fg="white", font=("Helvetica", 12)).grid(row=3, column=0, columnspan=2, pady=5)
        tk.Button(frame_produit, text="Supprimer Produit", command=self.supprimer_produit, bg="gray", fg="white", font=("Helvetica", 12)).grid(row=4, column=0, columnspan=2, pady=5)

        self.treeview_produits = ttk.Treeview(self.tab_produits, columns=("ID", "Nom", "Quantité"), show="headings")
        self.treeview_produits.heading("ID", text="ID")
        self.treeview_produits.heading("Nom", text="Nom")
        self.treeview_produits.heading("Quantité", text="Quantité")
        self.treeview_produits.pack(pady=10)

    def create_client_widgets(self):
        frame_client = ttk.Frame(self.tab_clients)
        frame_client.pack(pady=10, padx=10)

        tk.Label(frame_client, text="Nom du client", font=("Helvetica", 12)).grid(row=0, column=0, padx=5, pady=5)
        self.nom_client_entry = tk.Entry(frame_client, font=("Helvetica", 12), width=30)
        self.nom_client_entry.grid(row=0, column=1)

        tk.Label(frame_client, text="Adresse", font=("Helvetica", 12)).grid(row=1, column=0, padx=5, pady=5)
        self.adresse_entry = tk.Entry(frame_client, font=("Helvetica", 12), width=30)
        self.adresse_entry.grid(row=1, column=1)

        tk.Button(frame_client, text="Ajouter Client", command=self.ajouter_client, bg="gray", fg="white", font=("Helvetica", 12)).grid(row=2, column=0, pady=10, columnspan=2)
        tk.Button(frame_client, text="Afficher Clients", command=self.afficher_clients, bg="gray", fg="white", font=("Helvetica", 12)).grid(row=3, column=0, pady=5, columnspan=2)
        tk.Button(frame_client, text="Rechercher Client", command=self.rechercher_client, bg="gray", fg="white", font=("Helvetica", 12)).grid(row=4, column=0, pady=5, columnspan=2)
        tk.Button(frame_client, text="Supprimer Client", command=self.supprimer_client, bg="gray", fg="white", font=("Helvetica", 12)).grid(row=5, column=0, pady=5, columnspan=2)
        tk.Button(frame_client, text="Clear", command=self.clear_entries, bg="gray", fg="white", font=("Helvetica", 12)).grid(row=2, column=1, pady=10, sticky="e")

        self.treeview_clients = ttk.Treeview(self.tab_clients, columns=("ID", "Nom", "Adresse"), show="headings")
        self.treeview_clients.heading("ID", text="ID")
        self.treeview_clients.heading("Nom", text="Nom")
        self.treeview_clients.heading("Adresse", text="Adresse")
        self.treeview_clients.pack()

    def create_order_widgets(self):
        frame_commande = ttk.Frame(self.tab_commandes)
        frame_commande.pack(pady=10, padx=10)

        tk.Label(frame_commande, text="ID Client", font=("Helvetica", 12)).grid(row=0, column=0, padx=5, pady=5)
        self.client_id_entry = tk.Entry(frame_commande, font=("Helvetica", 12), width=30)
        self.client_id_entry.grid(row=0, column=1)

        tk.Label(frame_commande, text="Produit", font=("Helvetica", 12)).grid(row=1, column=0, padx=5, pady=5)
        self.produit_commande_entry = tk.Entry(frame_commande, font=("Helvetica", 12), width=30)
        self.produit_commande_entry.grid(row=1, column=1)

        tk.Label(frame_commande, text="Quantité", font=("Helvetica", 12)).grid(row=2, column=0, padx=5, pady=5)
        self.quantite_commande_entry = tk.Entry(frame_commande, font=("Helvetica", 12), width=30)
        self.quantite_commande_entry.grid(row=2, column=1)

        tk.Button(frame_commande, text="Ajouter Commande", command=self.ajouter_commande, bg="gray", fg="white", font=("Helvetica", 12)).grid(row=3, column=0, pady=10, columnspan=2)
        tk.Button(frame_commande, text="Afficher Commandes", command=self.afficher_commandes, bg="gray", fg="white", font=("Helvetica", 12)).grid(row=4, column=0, pady=5, columnspan=2)
        tk.Button(frame_commande, text="Rechercher Commande", command=self.rechercher_commande, bg="gray", fg="white", font=("Helvetica", 12)).grid(row=5, column=0, pady=5, columnspan=2)
        tk.Button(frame_commande, text="Supprimer Commande", command=self.supprimer_commande, bg="gray", fg="white", font=("Helvetica", 12)).grid(row=6, column=0, pady=5, columnspan=2)
        tk.Button(frame_commande, text="Clear", command=self.clear_entries, bg="gray", fg="white", font=("Helvetica", 12)).grid(row=4, column=1, pady=10, sticky="e")

        self.treeview_commandes = ttk.Treeview(self.tab_commandes, columns=("ID", "Client ID", "Produit", "Quantité", "Date"), show="headings")
        self.treeview_commandes.heading("ID", text="ID")
        self.treeview_commandes.heading("Client ID", text="Client ID")
        self.treeview_commandes.heading("Produit", text="Produit")
        self.treeview_commandes.heading("Quantité", text="Quantité")
        self.treeview_commandes.heading("Date", text="Date")
        self.treeview_commandes.pack()

    def clear_entries(self):
        self.nom_produit_entry.delete(0, tk.END)
        self.quantite_produit_entry.delete(0, tk.END)
        self.nom_client_entry.delete(0, tk.END)
        self.adresse_entry.delete(0, tk.END)
        self.client_id_entry.delete(0, tk.END)
        self.produit_commande_entry.delete(0, tk.END)
        self.quantite_commande_entry.delete(0, tk.END)


    def create_restore_widgets(self):
        frame_restaurer = ttk.Frame(self.tab_restaurer)
        frame_restaurer.pack(pady=10, padx=10)

        tk.Button(frame_restaurer, text="Restaurer la base de données", command=self.restaurer_db, bg="red", fg="white", font=("Helvetica", 12)).pack(pady=10)

    def ajouter_produit(self):
        nom = self.nom_produit_entry.get()
        quantite = self.quantite_produit_entry.get()

        if not quantite.isdigit():
            messagebox.showerror("Erreur", "La quantité doit être un entier.")
            return

        self.db.ajouter_produit(nom, int(quantite))
        self.afficher_produits()

    def afficher_produits(self):
        for i in self.treeview_produits.get_children():
            self.treeview_produits.delete(i)
        produits = self.db.afficher_produits()
        for produit in produits:
            self.treeview_produits.insert("", "end", values=produit)

    def rechercher_produit(self):
        keyword = self.nom_produit_entry.get()
        produits = self.db.rechercher_produit(keyword)
        for i in self.treeview_produits.get_children():
            self.treeview_produits.delete(i)
        for produit in produits:
            self.treeview_produits.insert("", "end", values=produit)

    def supprimer_produit(self):
        selected_item = self.treeview_produits.selection()[0]
        produit_id = self.treeview_produits.item(selected_item)['values'][0]
        self.db.supprimer_produit(produit_id)
        self.afficher_produits()

    def ajouter_client(self):
        nom = self.nom_client_entry.get()
        adresse = self.adresse_entry.get()
        self.db.ajouter_client(nom, adresse)
        self.afficher_clients()

    def afficher_clients(self):
        for i in self.treeview_clients.get_children():
            self.treeview_clients.delete(i)
        clients = self.db.afficher_clients()
        for client in clients:
            self.treeview_clients.insert("", "end", values=client)

    def rechercher_client(self):
        keyword = self.nom_client_entry.get()
        clients = self.db.rechercher_client(keyword)
        for i in self.treeview_clients.get_children():
            self.treeview_clients.delete(i)
        for client in clients:
            self.treeview_clients.insert("", "end", values=client)

    def supprimer_client(self):
        selected_item = self.treeview_clients.selection()[0]
        client_id = self.treeview_clients.item(selected_item)['values'][0]
        self.db.supprimer_client(client_id)
        self.afficher_clients()

    def ajouter_commande(self):
        client_id = self.client_id_entry.get()
        produit = self.produit_commande_entry.get()
        quantite = self.quantite_commande_entry.get()
        date_commande = datetime.datetime.now()

        if not quantite.isdigit():
            messagebox.showerror("Erreur", "La quantité doit être un entier.")
            return

        success = self.db.ajouter_commande(client_id, produit, int(quantite), date_commande)
        if success:
            messagebox.showinfo("Succès", "Commande ajoutée avec succès.")
            self.afficher_commandes()
        else:
            messagebox.showerror("Erreur", "Erreur lors de l'ajout de la commande.")

    def afficher_commandes(self):
        for i in self.treeview_commandes.get_children():
            self.treeview_commandes.delete(i)
        commandes = self.db.afficher_commandes()
        for commande in commandes:
            self.treeview_commandes.insert("", "end", values=commande)

    def rechercher_commande(self):
        keyword = self.produit_commande_entry.get()
        commandes = self.db.rechercher_commande(keyword)
        for i in self.treeview_commandes.get_children():
            self.treeview_commandes.delete(i)
        for commande in commandes:
            self.treeview_commandes.insert("", "end", values=commande)

    def supprimer_commande(self):
        selected_item = self.treeview_commandes.selection()[0]
        commande_id = self.treeview_commandes.item(selected_item)['values'][0]
        self.db.supprimer_commande(commande_id)
        self.afficher_commandes()

    def restaurer_db(self):
        self.db.restaurer()
        messagebox.showinfo("Succès", "Base de données restaurée avec succès.")
        # Rafraîchir les tableaux
        self.afficher_produits()
        self.afficher_clients()
        self.afficher_commandes()

if __name__ == "__main__":
    root = tk.Tk()
    db = Database()
    app = App(root, db)
    root.mainloop()
