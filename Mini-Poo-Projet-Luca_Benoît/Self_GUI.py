# Self_GUI.py
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from Self_XML_parser import ChargementXML


class FenetreChoix3D(ctk.CTkToplevel):
    """Fenêtre de dialogue pour choisir les deux axes de la nappe 3D.
    Utilisée quand le problème a plus de 2 variables d'entrée."""

    def __init__(self, parent, noms_entrees: list):
        super().__init__(parent)
        self.title("Choix des axes")
        self.geometry("350x200")
        self.resizable(False, False)
        self.grab_set()  # bloque la fenêtre principale pendant le choix

        ## Résultat du choix (None si annulé)
        self.axe_x = None
        self.axe_y = None

        ctk.CTkLabel(self, text="Choisir les deux axes de la nappe 3D :",
                     font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(15, 5))

        ## Axe X
        frame_x = ctk.CTkFrame(self, fg_color="transparent")
        frame_x.pack(fill=tk.X, padx=20, pady=5)
        ctk.CTkLabel(frame_x, text="Axe X :").pack(side=tk.LEFT, padx=(0, 10))
        self.choix_x = ctk.CTkComboBox(frame_x, values=noms_entrees)
        self.choix_x.set(noms_entrees[0])
        self.choix_x.pack(side=tk.LEFT)

        ## Axe Y
        frame_y = ctk.CTkFrame(self, fg_color="transparent")
        frame_y.pack(fill=tk.X, padx=20, pady=5)
        ctk.CTkLabel(frame_y, text="Axe Y :").pack(side=tk.LEFT, padx=(0, 10))
        self.choix_y = ctk.CTkComboBox(frame_y, values=noms_entrees)
        self.choix_y.set(noms_entrees[1])
        self.choix_y.pack(side=tk.LEFT)

        ## Bouton valider
        ctk.CTkButton(self, text="Générer la nappe", command=self.valider).pack(pady=15)

    def valider(self):
        """Vérifie que les deux axes sont différents et ferme la fenêtre."""
        x = self.choix_x.get()
        y = self.choix_y.get()
        if x == y:
            messagebox.showwarning("Attention", "Les deux axes doivent être différents.", parent=self)
            return
        self.axe_x = x
        self.axe_y = y
        self.destroy()


class GUI_POO(ctk.CTk):
    """Interface principale du moteur de logique floue."""

    def __init__(self):
        super().__init__()
        self.title("MINI POO - Système Fuzzy")
        self.geometry("1000x600")
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.systeme = None       # contiendra le FuzzySystem chargé
        self.sliders = {}         # {nom_variable: CTkSlider}
        self.labels_valeur = {}   # {nom_variable: CTkLabel} valeur courante du slider
        self.labels_sortie = {}   # {nom_variable: CTkLabel} résultats

        ## Panneau latéral (boutons)
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=10)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(3, weight=1)

        ctk.CTkLabel(self.sidebar, text="Système Fuzzy",
                     font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, padx=20, pady=(20, 10))
        ctk.CTkButton(self.sidebar, text="Charger Fichier XML",
                      command=self.choix_fichier_xml).grid(row=1, column=0, padx=20, pady=10)
        ctk.CTkButton(self.sidebar, text="Afficher nappe 3D",
                      command=self.afficher_plot_3d).grid(row=2, column=0, padx=20, pady=10)

        ## Panneau principal : côté entrées | côté sorties
        self.panneau_principal = ctk.CTkFrame(self, corner_radius=10)
        self.panneau_principal.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.panneau_principal.grid_columnconfigure(0, weight=1)
        self.panneau_principal.grid_columnconfigure(1, weight=1)
        self.panneau_principal.grid_rowconfigure(0, weight=1)

        ## Panneau entrées
        self.panneau_entree = ctk.CTkFrame(self.panneau_principal, corner_radius=10)
        self.panneau_entree.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        ctk.CTkLabel(self.panneau_entree, text="Paramètres d'entrée",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

        ## Panneau sorties
        self.panneau_sortie = ctk.CTkFrame(self.panneau_principal, corner_radius=10)
        self.panneau_sortie.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        ctk.CTkLabel(self.panneau_sortie, text="Résultats (Concrétisation)",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

    ## --- Fonctions des boutons du panneau latéral ---

    def choix_fichier_xml(self):
        """Ouvre un sélecteur de fichier et charge le XML choisi."""
        chemin = filedialog.askopenfilename(
            title="Choisir un fichier XML",
            filetypes=[("Fichiers XML", "*.xml")]
        )
        if chemin:
            self.chargement_xml(chemin)

    def chargement_xml(self, chemin: str):
        """Charge le fichier XML via le parser et reconstruit l'interface."""
        try:
            self.systeme = ChargementXML(chemin)
            self.construction_interface()
            messagebox.showinfo("Succès", "Fichier XML chargé avec succès !")
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger le fichier :\n{e}")

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
            ctk.CTkLabel(ligne_haut, text=f"{nom} ({var.unit}) :").pack(side=tk.LEFT)
            lbl_val = ctk.CTkLabel(ligne_haut, text=f"{var.min_val:.1f}")
            lbl_val.pack(side=tk.RIGHT)
            self.labels_valeur[nom] = lbl_val

            # Slider
            slider = ctk.CTkSlider(
                frame,
                from_=var.min_val,
                to=var.max_val,
                command=lambda val, n=nom: self.maj_valeur_slider(n, val)
            )
            slider.set(var.min_val)
            slider.pack(fill=tk.X, padx=5, pady=(0, 5))
            self.sliders[nom] = slider

        ## Création des labels de résultat pour chaque variable de sortie
        for nom, var in self.systeme.outputs.items():
            frame = ctk.CTkFrame(self.panneau_sortie, corner_radius=8)
            frame.pack(fill=tk.X, padx=10, pady=5)

            ctk.CTkLabel(frame, text=f"{nom} ({var.unit}) :").pack(side=tk.LEFT, padx=10)
            lbl_res = ctk.CTkLabel(frame, text="---", font=ctk.CTkFont(size=14, weight="bold"))
            lbl_res.pack(side=tk.RIGHT, padx=10)
            self.labels_sortie[nom] = lbl_res

        ## Premier calcul avec les valeurs initiales
        self.update_results()

    def maj_valeur_slider(self, nom: str, valeur: float):
        """Met à jour l'affichage de la valeur du slider et relance le calcul."""
        self.labels_valeur[nom].configure(text=f"{float(valeur):.2f}")
        self.update_results()

    def update_results(self):
        """Récupère les valeurs des sliders, calcule et affiche les résultats."""
        if self.systeme is None:
            return

        input_values = {nom: slider.get() for nom, slider in self.sliders.items()}
        resultats = self.systeme.compute(input_values)

        for nom, valeur in resultats.items():
            if nom in self.labels_sortie:
                self.labels_sortie[nom].configure(
                    text=f"{valeur:.2f} {self.systeme.outputs[nom].unit}"
                )

    ## --- Visualisation nappe 3D ---

    def afficher_plot_3d(self):
        """Génère la ou les nappes 3D de surface réponse du problème chargé."""
        if self.systeme is None:
            messagebox.showwarning("Attention", "Veuillez d'abord charger un fichier XML.")
            return

        noms_entrees = list(self.systeme.inputs.keys())

        ## Si plus de 2 entrées : demander à l'utilisateur de choisir les 2 axes
        if len(noms_entrees) > 2:
            fenetre_choix = FenetreChoix3D(self, noms_entrees)
            self.wait_window(fenetre_choix)  # attend que l'utilisateur ferme la fenêtre

            ## Si l'utilisateur a annulé (fermé sans valider)
            if fenetre_choix.axe_x is None:
                return
            nom_axe_x = fenetre_choix.axe_x
            nom_axe_y = fenetre_choix.axe_y
        else:
            ## Exactement 2 entrées : on les prend directement
            nom_axe_x = noms_entrees[0]
            nom_axe_y = noms_entrees[1]

        ## Récupération des objets variables pour les deux axes choisis
        var_x = self.systeme.inputs[nom_axe_x]
        var_y = self.systeme.inputs[nom_axe_y]

        ## Valeurs fixes pour les entrées non affichées (on prend la valeur du slider)
        valeurs_fixes = {nom: slider.get() for nom, slider in self.sliders.items()}

        ## Discrétisation des deux axes (30 points = bon compromis rapidité/précision)
        nb_points = 30
        valeurs_x = np.linspace(var_x.min_val, var_x.max_val, nb_points)
        valeurs_y = np.linspace(var_y.min_val, var_y.max_val, nb_points)

        ## Grille des combinaisons (X, Y)
        grille_x, grille_y = np.meshgrid(valeurs_x, valeurs_y)

        ## Calcul d'une nappe par variable de sortie
        for nom_sortie in self.systeme.outputs.keys():

            ## Tableau qui contiendra les valeurs de sortie pour chaque point de la grille
            grille_z = np.zeros((nb_points, nb_points))

            for i in range(nb_points):
                for j in range(nb_points):
                    ## Construction du dictionnaire d'entrées pour ce point de la grille
                    input_point = dict(valeurs_fixes)  # copie des valeurs fixes
                    input_point[nom_axe_x] = valeurs_x[j]
                    input_point[nom_axe_y] = valeurs_y[i]

                    ## Calcul du moteur flou pour ce point
                    resultats = self.systeme.compute(input_point)
                    grille_z[i, j] = resultats[nom_sortie]

            ## Affichage dans une nouvelle fenêtre matplotlib
            self._afficher_nappe(nom_axe_x, nom_axe_y, nom_sortie,
                                 grille_x, grille_y, grille_z)

        plt.show()

    def _afficher_nappe(self, nom_x: str, nom_y: str, nom_sortie: str,
                        grille_x, grille_y, grille_z):
        """Crée une figure matplotlib avec la nappe 3D pour une variable de sortie."""
        var_x = self.systeme.inputs[nom_x]
        var_y = self.systeme.inputs[nom_y]
        var_sortie = self.systeme.outputs[nom_sortie]

        fig = plt.figure(figsize=(9, 6))
        fig.canvas.manager.set_window_title(f"Nappe 3D — {nom_sortie}")

        ax = fig.add_subplot(111, projection='3d')

        ## Tracé de la surface
        surface = ax.plot_surface(grille_x, grille_y, grille_z,
                                  cmap=cm.viridis, alpha=0.85)

        ## Légendes des axes
        ax.set_xlabel(f"{nom_x} ({var_x.unit})")
        ax.set_ylabel(f"{nom_y} ({var_y.unit})")
        ax.set_zlabel(f"{nom_sortie} ({var_sortie.unit})")
        ax.set_title(f"Surface réponse : {nom_sortie}\n"
                     f"(axe X = {nom_x}, axe Y = {nom_y})")

        ## Barre de couleur
        fig.colorbar(surface, ax=ax, shrink=0.5, label=f"{nom_sortie} ({var_sortie.unit})")


## Point d'entrée direct
if __name__ == "__main__":
    app = GUI_POO()
    app.mainloop()
