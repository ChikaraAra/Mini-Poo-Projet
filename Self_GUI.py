import tkinter as tk
import customtkinter as ctk
from Self_XML_parser import ChargementXML
class GUI_POO(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("MINI POO - Système Fuzzy")
        self.sliders = {}
        self.geometry("1000x600")
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        ## definition d'un panneau latéral pour les boutons
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=10)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(0, weight=1)

        ctk.CTkLabel(self.sidebar, text="Système Fuzzy", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, padx=20, pady=(20, 10))
        ctk.CTkButton(self.sidebar, text="Charger Fichier XML", command=self.choix_fichier_xml).grid(row=1, column=0, padx=20, pady=10)
        ctk.CTkButton(self.sidebar, text="Afficher visualisation (plot)", command=self.afficher_plot).grid(row=2, column=0, padx=20, pady=10)
        ctk.CTkButton(self.sidebar, text="Afficher visualisation (3D)", command=self.afficher_plot_3d).grid(row=3, column=0, padx=20, pady=10)

        ## definition d'un panneau principal divisé en deux parties : une pour les sliders d'entrée et une pour la sortie
        self.panneau_principal = ctk.CTkFrame(self, corner_radius=10)
        self.panneau_principal.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.panneau_principal.grid_columnconfigure(0, weight=1)
        self.panneau_principal.grid_rowconfigure(0, weight=1)
        self.panneau_entrée = ctk.CTkFrame(self.panneau_principal, corner_radius=10)

        ctk.CTkLabel(self.panneau_entrée, text="Paramètres d'entrée", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        self.panneau_entrée.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.panneau_entrée.grid_rowconfigure(0, weight=1)
        self.panneau_sortie = ctk.CTkFrame(self.panneau_principal, corner_radius=10)

        ctk.CTkLabel(self.panneau_sortie, text="Résultats (Concrétisation)", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        self.panneau_sortie.grid(row=0, column=1, sticky="nsew",  padx=10, pady=10)
        self.panneau_sortie.grid_rowconfigure(0, weight=1)
        

    ## definition des fonctions pour les boutons du panneau latéral

    ## definition de la fonctions pour choisir le fichier XML
    def choix_fichier_xml(self):
        chemin = tk.filedialog.askopenfilename(title="Choisir un fichier XML", filetypes=[("Fichiers XML", "*.xml")])
        if chemin:
            self.chargement_xml(chemin)       

    ## definition cHargement du fichier XML et stockage des variables d'entrée, de sortie et des règles
    def chargement_xml(self,chemin: str):
        self.input_variables, self.output_variables, self.rules = ChargementXML(chemin)
        print("Variables d'entrée :", self.input_variables)
        self.construction_interface_input()

    ##definition de la focntion de creation des sliders d'entrée et de la visualisation de la sortie
    def construction_interface_input(self):
        ##Nettoyage des anciens sliders en input

        for widget in self.panneau_entrée.winfo_children():
            if isinstance(widget, ctk.CTkSlider):
                widget.destroy()
        self.sliders.clear()
        

        ##Creation des sliders d'entrée
        for name, var in self.input_variables.items():
            frame = ctk.CTkFrame(self.panneau_entrée, corner_radius=10)
            frame.pack(fill=tk.X, pady=5)
            ctk.CTkLabel(frame, text=f"{name} ({var}) :", width=20, anchor="w").pack(side=tk.LEFT)
            
            slider = ctk.CTkSlider(frame, from_=var['min'], to=var['max'], orient=tk.HORIZONTAL, resolution=0.1, command=self.update_results)
            slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.sliders[name] = slider


    ##definition des fonctions pour afficher les visualisations (plot et 3D)
    def afficher_plot(self):
        pass

    def afficher_plot_3d(self):
        pass


app = GUI_POO()
app.mainloop()






        



