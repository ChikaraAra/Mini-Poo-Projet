# fuzzy_gui.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from fuzzy_parser import parse_xml

class FuzzyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Moteur Logique Floue - Projet 2025_S2")
        self.system = None
        self.sliders = {}

        # Frame de contrôle (Bouton chargement)
        control_frame = tk.Frame(root, pady=10)
        control_frame.pack(fill=tk.X)
        tk.Button(control_frame, text="Charger Fichier XML", command=self.load_file).pack()

        # Frame d'entrées (Sliders)
        self.inputs_frame = tk.LabelFrame(root, text="Paramètres d'Entrée", padx=10, pady=10)
        self.inputs_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Frame de résultats
        self.results_frame = tk.LabelFrame(root, text="Résultats (Concrétisation)", padx=10, pady=10)
        self.results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def load_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("XML files", "*.xml")])
        if filepath:
            try:
                self.system = parse_xml(filepath)
                self.build_ui()
                messagebox.showinfo("Succès", "Fichier XML chargé avec succès !")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la lecture du fichier : {e}")

    def build_ui(self):
        # Nettoyer les anciens widgets
        for widget in self.inputs_frame.winfo_children(): widget.destroy()
        for widget in self.results_frame.winfo_children(): widget.destroy()
        self.sliders.clear()

        # Générer dynamiquement les sliders pour chaque entrée
        for name, var in self.system.inputs.items():
            frame = tk.Frame(self.inputs_frame)
            frame.pack(fill=tk.X, pady=5)
            tk.Label(frame, text=f"{name} ({var.unit}) :", width=20, anchor="w").pack(side=tk.LEFT)
            
            slider = tk.Scale(frame, from_=var.min_val, to=var.max_val, orient=tk.HORIZONTAL, resolution=0.1, command=self.update_results)
            slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.sliders[name] = slider

        # Générer les labels de résultats
        self.result_labels = {}
        for name, var in self.system.outputs.items():
            frame = tk.Frame(self.results_frame)
            frame.pack(fill=tk.X, pady=5)
            tk.Label(frame, text=f"{name} ({var.defuzzification}/{var.aggregation}):", width=30, anchor="w", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
            lbl = tk.Label(frame, text="0.00", font=("Arial", 10))
            lbl.pack(side=tk.LEFT)
            self.result_labels[name] = lbl

        self.update_results() # Premier calcul initial

    def update_results(self, event=None):
        """Appelée à chaque mouvement d'un slider."""
        if not self.system: return
        
        # Récupérer les valeurs des inputs
        input_values = {name: slider.get() for name, slider in self.sliders.items()}
        
        # Lancer le calcul flou
        results = self.system.compute(input_values)
        
        # Afficher les résultats
        for name, value in results.items():
            self.result_labels[name].config(text=f"{value:.2f}")