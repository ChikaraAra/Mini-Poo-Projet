# Classes_MP.py
import numpy as np
from fonction_math_MP import Triangulaire, Trapezoidale, Gaussienne, DemiTrapezeGauche, DemiTrapezeDroite


class FuzzySet:
    """Définit un ensemble flou (ex: 'Froid', 'Chaud') et sa loi mathématique."""

    def __init__(self, name: str, set_type: str, params: dict):
        self.name = name
        self.set_type = set_type
        self.params = params

    def get_appartenance(self, x: float) -> float:
        """Retourne le degré d'appartenance µ pour une valeur x (entre 0 et 1)."""
        t = self.set_type

        if t in ("triangular", "triangulaire"):
            return Triangulaire(self.params['a'], self.params['b'], self.params['c'])(x)

        elif t in ("trapezoidal", "trapezoidale"):
            # 4 paramètres distincts : a, b, c, d
            return Trapezoidale(self.params['a'], self.params['b'],
                                self.params['c'], self.params['d'])(x)

        elif t in ("half_trapezoidal", "demi_trapeze"):
            # 'a' vaut "left" (demi-trapèze gauche) ou "right" (demi-trapèze droit)
            # b = fin du plateau / début de pente, c = fin de la pente
            cote = self.params.get('a', 'left')
            b = self.params['b']
            c = self.params['c']
            if cote == 'left':
                return DemiTrapezeGauche(b, c)(x)
            else:
                return DemiTrapezeDroite(b, c)(x)

        elif t in ("gaussian", "gaussienne"):
            return Gaussienne(self.params['moyenne'], self.params['ecart_type'])(x)

        return 0.0


class Variable:
    """Classe parente pour les variables d'entrée et de sortie."""

    def __init__(self, name: str, min_val: float, max_val: float, unit: str = ""):
        self.name = name
        self.min_val = min_val
        self.max_val = max_val
        self.unit = unit
        self.fuzzy_sets = {}  # Dictionnaire {nom_ensemble: objet FuzzySet}

    def add_set(self, fuzzy_set: FuzzySet):
        """Ajoute un ensemble flou à la variable."""
        self.fuzzy_sets[fuzzy_set.name] = fuzzy_set


class InputVariable(Variable):
    """Paramètre d'entrée réel."""

    def fuzzify(self, valeur: float) -> dict:
        """Étape 1 — Fuzzification : calcule µ de valeur pour chaque ensemble flou."""
        return {nom: fset.get_appartenance(valeur) for nom, fset in self.fuzzy_sets.items()}


class OutputVariable(Variable):
    """Paramètre de sortie : nécessite agrégation et défuzzification."""

    def __init__(self, name: str, val_min: float, val_max: float, unite: str,
                 nb_points: int, aggregation: str, defuzzification: str):
        super().__init__(name, val_min, val_max, unite)
        self.nb_points = int(nb_points)
        self.aggregation = aggregation        # "Max" ou "Sum"
        self.defuzzification = defuzzification  # "CoG" ou "MoM"
        # Discrétisation du domaine pour l'agrégation
        self.x_domain = np.linspace(val_min, val_max, self.nb_points)

    def defuzzify(self, courbe: np.ndarray) -> float:
        """Étape 4 — Concrétisation à partir de la courbe agrégée (CoG ou MoM)."""
        sum_mu = np.sum(courbe)

        # Si aucune règle activée, on retourne le centre du domaine
        if sum_mu == 0:
            return float((self.min_val + self.max_val) / 2)

        if self.defuzzification == "CoG":
            # Centre de gravité
            return float(np.sum(self.x_domain * courbe) / sum_mu)

        elif self.defuzzification == "MoM":
            # Moyenne des maximums
            max_val = np.max(courbe)
            indices = np.where(courbe == max_val)[0]
            return float(np.mean(self.x_domain[indices]))

        # Par défaut CoG
        return float(np.sum(self.x_domain * courbe) / sum_mu)


class Rule:
    """Représente une règle floue : prémisses -> conclusions."""

    def __init__(self, rule_id: str, description: str, premise_tree: dict, conclusions: list):
        self.id = rule_id
        self.description = description
        self.premise_tree = premise_tree  # Arbre récursif de conditions
        self.conclusions = conclusions    # Liste de tuples (nom_var_sortie, nom_ensemble)

    def evaluate_premise(self, node: dict, fuzzified_inputs: dict) -> float:
        """Étape 2 — Inférence : évalue récursivement l'arbre de prémisses."""
        # Cas feuille : clause simple sur une variable
        if 'variable' in node:
            var_name = node['variable']
            set_name = node['set']
            if var_name not in fuzzified_inputs:
                return 0.0
            return fuzzified_inputs[var_name].get(set_name, 0.0)

        # Cas nœud : opérateur logique
        op = node['operator']

        if op == "NOT":
            return 1.0 - self.evaluate_premise(node['children'][0], fuzzified_inputs)

        val1 = self.evaluate_premise(node['children'][0], fuzzified_inputs)
        val2 = self.evaluate_premise(node['children'][1], fuzzified_inputs)

        if op == "AND":
            return min(val1, val2)
        elif op == "OR":
            return max(val1, val2)
        elif op == "XOR":
            return max(val1, val2) - min(val1, val2)

        return 0.0


class FuzzySystem:
    """Le moteur flou principal : variables d'entrée, de sortie et règles."""

    def __init__(self):
        self.inputs = {}   # {nom: InputVariable}
        self.outputs = {}  # {nom: OutputVariable}
        self.rules = []    # Liste de Rule

    def compute(self, input_values: dict) -> dict:
        """Orchestre les 4 étapes : fuzzification, inférence, agrégation, défuzzification."""

        # Étape 1 : Fuzzification
        fuzzified = {}
        for nom, var in self.inputs.items():
            fuzzified[nom] = var.fuzzify(input_values[nom])

        # Étape 2 : Inférence des règles
        rule_results = []  # liste de (nom_var_sortie, nom_ensemble, degré_vérité)
        for rule in self.rules:
            truth_value = rule.evaluate_premise(rule.premise_tree, fuzzified)
            if truth_value > 0:
                for out_var, out_set in rule.conclusions:
                    rule_results.append((out_var, out_set, truth_value))

        # Étapes 3 & 4 : Agrégation puis Défuzzification
        results = {}
        for out_name, out_var in self.outputs.items():
            # Courbe agrégée initialisée à zéro
            aggregated_curve = np.zeros(out_var.nb_points)

            relevant_results = [r for r in rule_results if r[0] == out_name]

            for _, set_name, truth_value in relevant_results:
                if set_name not in out_var.fuzzy_sets:
                    continue
                f_set = out_var.fuzzy_sets[set_name]

                # Courbe de l'ensemble flou discrétisée sur tout le domaine
                set_curve = np.array([f_set.get_appartenance(x) for x in out_var.x_domain])

                # Troncation par le degré de vérité de la prémisse
                truncated_curve = np.minimum(set_curve, truth_value)

                # Agrégation
                if out_var.aggregation == "Max":
                    aggregated_curve = np.maximum(aggregated_curve, truncated_curve)
                elif out_var.aggregation == "Sum":
                    aggregated_curve = aggregated_curve + truncated_curve

            # Défuzzification
            results[out_name] = out_var.defuzzify(aggregated_curve)

        return results
