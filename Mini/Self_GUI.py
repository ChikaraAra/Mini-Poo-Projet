# Self_GUI.py
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from Self_XML_parser import ChargementXML


class ChoixDesAxes(ctk.CTkToplevel):
    """Fenêtre de sélection des axes pour la nappe 3D."""

    def __init__(self, parent, noms_entrees: list):
        super().__init__(parent)
        self.title("Choix des axes")
        self.geometry("350x200")
        self.resizable(False, False)
        self.grab_set()  # Bloquer la fenêtre principale

        self.axe_x = None
        self.axe_y = None

        ctk.CTkLabel(self, text="Choisir les deux axes de la nappe 3D :", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(15, 5))

        # Choix de l'axe X
        frame_x = ctk.CTkFrame(self, fg_color="transparent")
        frame_x.pack(fill=tk.X, padx=20, pady=5)
        ctk.CTkLabel(frame_x, text="Axe X :").pack(side=tk.LEFT, padx=(0, 10))
        self.choix_x = ctk.CTkComboBox(frame_x, values=noms_entrees)
        self.choix_x.set(noms_entrees[0])
        self.choix_x.pack(side=tk.LEFT)

        # Choix de l'axe Y
        frame_y = ctk.CTkFrame(self, fg_color="transparent")
        frame_y.pack(fill=tk.X, padx=20, pady=5)
        ctk.CTkLabel(frame_y, text="Axe Y :").pack(side=tk.LEFT, padx=(0, 10))
        self.choix_y = ctk.CTkComboBox(frame_y, values=noms_entrees)
        self.choix_y.set(noms_entrees[1])
        self.choix_y.pack(side=tk.LEFT)

        ## Bouton valider
        ctk.CTkButton(self, text="Générer la nappe", command=self.valider).pack(pady=15)

    def valider(self):
        """Vérifier que les axes sont différents et fermer."""
        x = self.choix_x.get()
        y = self.choix_y.get()
        if x == y:
            messagebox.showwarning("Attention", "Les deux axes doivent être différents.", parent=self)
            return
        self.axe_x = x
        self.axe_y = y
        self.destroy()


class GUI_POO(ctk.CTk):
    """Interface graphique du système flou."""

    def __init__(self):
        super().__init__()
        self.title("MINI POO - Système Fuzzy")
        self.geometry("1000x600")
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.systeme = None
        self.sliders = {}
        self.labels_valeur = {}
        self.labels_sortie = {}

        # Panneau latéral avec boutons
        self.panneau_lateral = ctk.CTkFrame(self, width=200, corner_radius=10)
        self.panneau_lateral.grid(row=0, column=0, sticky="nsew")
        self.panneau_lateral.grid_rowconfigure(3, weight=1)

        ctk.CTkLabel(self.panneau_lateral, text="Système Fuzzy",font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, padx=20, pady=(20, 10))
        ctk.CTkButton(self.panneau_lateral, text="Charger Fichier XML",command=self.choix_fichier_xml).grid(row=1, column=0, padx=20, pady=10)
        ctk.CTkButton(self.panneau_lateral, text="Afficher nappe 3D",command=self.afficher_plot_3d).grid(row=2, column=0, padx=20, pady=10)

        # Panneau principal : entrées et sorties
        self.panneau_principal = ctk.CTkFrame(self, corner_radius=10)
        self.panneau_principal.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.panneau_principal.grid_columnconfigure(0, weight=1)
        self.panneau_principal.grid_columnconfigure(1, weight=1)
        self.panneau_principal.grid_rowconfigure(0, weight=1)

        # Panneau d'entrée
        self.panneau_entree = ctk.CTkFrame(self.panneau_principal, corner_radius=10)
        self.panneau_entree.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        ctk.CTkLabel(self.panneau_entree, text="Paramètres d'entrée",font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

        # Panneau de sortie
        self.panneau_sortie = ctk.CTkFrame(self.panneau_principal, corner_radius=10)
        self.panneau_sortie.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        ctk.CTkLabel(self.panneau_sortie, text="Résultats (Concrétisation)",font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

    ## --- Fonctions des boutons du panneau latéral ---

    def choix_fichier_xml(self):
        """Ouvrir un sélecteur de fichier XML."""
        chemin = filedialog.askopenfilename(title="Choisir un fichier XML")
        if chemin:
            self.chargement_xml(chemin)

    def chargement_xml(self, chemin: str):
        """Charger un fichier XML et reconstruire l'interface."""
        self.systeme = ChargementXML(chemin)
        self.construction_interface()

    ## --- Construction dynamique de l'interface après chargement XML ---

    def construction_interface(self):
        """Recrée les sliders d'entrée et les labels de sortie selon le problème chargé."""
        ## Nettoyage des anciens widgets
        for widget in self.panneau_entree.winfo_children():
            if not isinstance(widget, ctk.CTkLabel) or widget.cget("text") != "Paramètres d'entrée":
                widget.destroy()
        for widget in self.panneau_sortie.winfo_children():
            if not isinstance(widget, ctk.CTkLabel) or widget.cget("text") != "Résultats (Concrétisation)":
                widget.destroy()
        self.sliders.clear()
        self.labels_valeur.clear()
        self.labels_sortie.clear()

        ## Création des sliders pour chaque variable d'entrée
        for nom, var in self.systeme.inputs.items():
            frame = ctk.CTkFrame(self.panneau_entree, corner_radius=8)
            frame.pack(fill=tk.X, padx=10, pady=5)

            # Ligne du haut : nom + valeur actuelle
            ligne_haut = ctk.CTkFrame(frame, fg_color="transparent")
            ligne_haut.pack(fill=tk.X, padx=5, pady=(5, 0))
            ctk.CTkLabel(ligne_haut, text=f"{nom} ({var.unite}) :").pack(side=tk.LEFT)
            lbl_val = ctk.CTkLabel(ligne_haut, text=f"{var.val_min:.1f}")
            lbl_val.pack(side=tk.RIGHT)
            self.labels_valeur[nom] = lbl_val

            # Slider
            slider = ctk.CTkSlider(frame,from_=var.val_min,to=var.val_max,command=lambda val, n=nom: self.maj_valeur_slider(n, val))
            slider.set(var.val_min)
            slider.pack(fill=tk.X, padx=5, pady=(0, 5))
            self.sliders[nom] = slider

        for nom, var in self.systeme.outputs.items():
            frame = ctk.CTkFrame(self.panneau_sortie, corner_radius=8)
            frame.pack(fill=tk.X, padx=10, pady=5)

            ctk.CTkLabel(frame, text=f"{nom} ({var.unite}) :").pack(side=tk.LEFT, padx=10)
            lbl_res = ctk.CTkLabel(frame, text="---", font=ctk.CTkFont(size=14, weight="bold"))
            lbl_res.pack(side=tk.RIGHT, padx=10)
            self.labels_sortie[nom] = lbl_res

        ## Premier calcul avec les valeurs initiales
        self.relance_calcul()

    def maj_valeur_slider(self, nom: str, valeur: float):
        """Mettre à jour l'affichage et relancer le calcul."""
        self.labels_valeur[nom].configure(text=f"{float(valeur):.2f}")
        self.relance_calcul()

    def relance_calcul(self):
        """Exécuter le système flou et afficher les résultats."""
        if self.systeme is None:
            return

        input_values = {nom: slider.get() for nom, slider in self.sliders.items()}
        resultats = self.systeme.compute(input_values)

        for nom, valeur in resultats.items():
            if nom in self.labels_sortie:
                self.labels_sortie[nom].configure(text=f"{valeur:.2f} {self.systeme.outputs[nom].unite}")

    ## --- Visualisation nappe 3D ---

    def afficher_plot_3d(self):
        """Générer et afficher la nappe 3D."""
        if self.systeme is None:
            messagebox.showwarning("Attention", "Veuillez d'abord charger un fichier XML.")
            return

        noms_entrees = list(self.systeme.inputs.keys())
        if len(noms_entrees) < 2:
            messagebox.showwarning(
                "Attention", "Il faut au moins deux variables d'entrée pour tracer une nappe 3D.", parent=self,)
            return

        # Demander à l'utilisateur de choisir les axes
        fenetre_choix = ChoixDesAxes(self, noms_entrees)
        self.wait_window(fenetre_choix)

        if fenetre_choix.axe_x is None:
            return

        nom_axe_x = fenetre_choix.axe_x
        nom_axe_y = fenetre_choix.axe_y

        var_x = self.systeme.inputs[nom_axe_x]
        var_y = self.systeme.inputs[nom_axe_y]

        # Récupérer les valeurs actuelles des sliders
        valeurs_fixes = {nom: slider.get() for nom, slider in self.sliders.items()}

        # Discrétiser les deux axes
        nb_points = 30
        valeurs_x_pas_inv = np.linspace(var_x.val_min, var_x.val_max, nb_points)
        valeurs_x = valeurs_x_pas_inv[::-1]  # axe X normal
        valeurs_y = np.linspace(var_y.val_min, var_y.val_max, nb_points)

        grille_x, grille_y = np.meshgrid(valeurs_x, valeurs_y)

        # Calculer les nappes pour chaque sortie
        for nom_sortie in self.systeme.outputs.keys():
            grille_z = np.zeros((nb_points, nb_points))

            for i in range(nb_points):
                for j in range(nb_points):
                    input_point = dict(valeurs_fixes)
                    input_point[nom_axe_x] = valeurs_x[j]
                    input_point[nom_axe_y] = valeurs_y[i]

                    resultats = self.systeme.compute(input_point)
                    grille_z[i, j] = resultats[nom_sortie]

            self._afficher_nappe(nom_axe_x, nom_axe_y, nom_sortie, grille_x, grille_y, grille_z)

        plt.show()

    def _afficher_nappe(self, nom_x: str, nom_y: str, nom_sortie: str, grille_x, grille_y, grille_z):
        """Afficher une nappe 3D pour une variable de sortie."""
        var_x = self.systeme.inputs[nom_x]
        var_y = self.systeme.inputs[nom_y]
        var_sortie = self.systeme.outputs[nom_sortie]

        fig = plt.figure(figsize=(9, 6))
        fig.canvas.manager.set_window_title(f"Nappe 3D — {nom_sortie}")
        ax = fig.add_subplot(111, projection='3d')

        # Tracer la surface
        surface = ax.plot_surface(grille_x, grille_y, grille_z, cmap=cm.viridis, alpha=0.85)

        # Centrer les axes autour de 0
        val_x = max(abs(var_x.val_min), abs(var_x.val_max))
        val_y = max(abs(var_y.val_min), abs(var_y.val_max))
        ax.set_xlim(val_x, 0)
        ax.set_ylim(0, val_y)

        # Étiquetage
        ax.set_xlabel(f"{nom_x} ({var_x.unite})")
        ax.set_ylabel(f"{nom_y} ({var_y.unite})")
        ax.set_zlabel(f"{nom_sortie} ({var_sortie.unite})")
        ax.set_title(f"{nom_sortie}\n")

        # Barre de couleur
        fig.colorbar(surface, ax=ax, shrink=0.5, label=f"{nom_sortie} ({var_sortie.unite})")