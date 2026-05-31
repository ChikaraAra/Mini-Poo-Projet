# Classes_MP.py
import numpy as np
from fonction_math_MP import Triangulaire, Trapezoidale, Gaussienne, DemiTrapezeGauche, DemiTrapezeDroite


class FuzzySet:
    """Un ensemble flou avec son type et ses paramètres."""

    def __init__(self, name: str, type_ensemble: str, parametres: dict):
        self.name = name
        self.type_ensemble = type_ensemble
        self.parametres = parametres

    def get_appartenance(self, x: float) -> float:
        """Calcule le degré d'appartenance à cet ensemble (entre 0 et 1)."""
        t = self.type_ensemble

        if t in ("triangular", "triangulaire"):
            return Triangulaire(self.parametres['a'], self.parametres['b'], self.parametres['c'])(x)

        elif t in ("trapezoidal", "trapezoidale"):
            # 4 paramètres distincts : a, b, c, d
            return Trapezoidale(self.parametres['a'], self.parametres['b'],
                                self.parametres['c'], self.parametres['d'])(x)

        elif t in ("half_trapezoidal", "demi_trapeze"):
            cote = self.parametres.get('a', 'left')
            b = self.parametres['b']
            c = self.parametres['c']
            if cote == 'left':
                return DemiTrapezeGauche(b, c)(x)
            else:
                return DemiTrapezeDroite(b, c)(x)

        elif t in ("gaussian", "gaussienne"):
            return Gaussienne(self.parametres['moyenne'], self.parametres['ecart_type'])(x)

        return 0.0


class Variable:
    """Classe de base pour les variables d'entrée et de sortie."""

    def __init__(self, name: str, val_min: float, val_max: float, unite: str = ""):
        self.name = name
        self.val_min = val_min
        self.val_max = val_max
        self.unite = unite
        self.fuzzy_sets = {}  # Dictionnaire {nom_ensemble: objet FuzzySet}

    def add_set(self, fuzzy_set: FuzzySet):
        """Ajoute un ensemble flou à la variable."""
        self.fuzzy_sets[fuzzy_set.name] = fuzzy_set


class InputVariable(Variable):
    """Paramètre d'entrée réel."""

    def fuzzify(self, valeur: float) -> dict:
        """Convertit une valeur numérique en degrés d'appartenance aux ensembles flous."""
        return {nom: fset.get_appartenance(valeur) for nom, fset in self.fuzzy_sets.items()}


class OutputVariable(Variable):
    """Une variable de sortie qui nécessite agrégation et défuzzification."""

    def __init__(self, name: str, val_min: float, val_max: float, unite: str,
                 nb_points: int, aggregation: str, defuzzification: str):
        super().__init__(name, val_min, val_max, unite)
        self.nb_points = int(nb_points)
        self.aggregation = aggregation  # "Max" ou "Sum"
        self.defuzzification = defuzzification  # "CoG" ou "MoM"
        # Précalculer le domaine discrétisé
        self.domaine_x = np.linspace(val_min, val_max, self.nb_points)

    def defuzzify(self, courbe: np.ndarray) -> float:
        """Convertit une courbe d'appartenance en valeur numérique de sortie."""
        somme_mu = np.sum(courbe)

        # Si aucune règle ne s'active, retourner le centre
        if somme_mu == 0:
            return float((self.val_min + self.val_max) / 2)

        if self.defuzzification == "CoG":
            # Centre de gravité
            return float(np.sum(self.domaine_x * courbe) / somme_mu)

        elif self.defuzzification == "MoM":
            # Moyenne des maximums
            max_app = np.max(courbe)
            positions = np.where(courbe == max_app)[0]
            return float(np.mean(self.domaine_x[positions]))

        # Par défaut, utiliser CoG
        return float(np.sum(self.domaine_x * courbe) / somme_mu)


class Rule:
    """Une règle floue : conditions => conclusions."""

    def __init__(self, id_regle: str, description: str, arbre_premisse: dict, conclusions: list):
        self.id = id_regle
        self.description = description
        self.arbre_premisse = arbre_premisse  # Arbre des conditions
        self.conclusions = conclusions  # Tuples (variable_sortie, ensemble_flou)

    def evaluate_premise(self, node: dict, fuzzified_inputs: dict) -> float:
        """Evalue récursivement les conditions et retourne le degré de vérité."""
        # Si c'est une clause simple
        if 'variable' in node:
            var_name = node['variable']
            set_name = node['set']
            if var_name not in fuzzified_inputs:
                return 0.0
            return fuzzified_inputs[var_name].get(set_name, 0.0)

        # Si c'est un opérateur logique
        operateur = node['operator']

        if operateur == "NOT":
            return 1.0 - self.evaluate_premise(node['children'][0], fuzzified_inputs)

        val1 = self.evaluate_premise(node['children'][0], fuzzified_inputs)
        val2 = self.evaluate_premise(node['children'][1], fuzzified_inputs)

        if operateur == "AND":
            return min(val1, val2)
        elif operateur == "OR":
            return max(val1, val2)
        elif operateur == "XOR":
            return max(val1, val2) - min(val1, val2)

        return 0.0


class FuzzySystem:
    """Le moteur d'inférence flou : gère entrées, sorties et règles."""

    def __init__(self):
        self.inputs = {}  # Variables d'entrée
        self.outputs = {}  # Variables de sortie
        self.rules = []  # Règles de production

    def compute(self, input_values: dict) -> dict:
        """Exécute le cycle complet : fuzzification, inférence, agrégation, défuzzification."""

        #Fuzzification
        fuzzifie = {}
        for nom, var in self.inputs.items():
            fuzzifie[nom] = var.fuzzify(input_values[nom])

        #application rules
        rule_results = []  # Tuples (var_sortie, ensemble, degré)
        for rule in self.rules:
            truth_value = rule.evaluate_premise(rule.arbre_premisse, fuzzifie)
            if truth_value > 0:
                for out_var, out_set in rule.conclusions:
                    rule_results.append((out_var, out_set, truth_value))

        # 3 & 4. Agrégation et défuzzification
        results = {}
        for out_name, out_var in self.outputs.items():
            aggregated_curve = np.zeros(out_var.nb_points)
            relevant_results = [r for r in rule_results if r[0] == out_name]

            for _, set_name, truth_value in relevant_results:
                if set_name not in out_var.fuzzy_sets:
                    continue
                f_set = out_var.fuzzy_sets[set_name]

                # Courbe de l'ensemble flou
                set_curve = np.array([f_set.get_appartenance(x) for x in out_var.domaine_x])
                # Tronquer par le degré de vérité
                truncated_curve = np.minimum(set_curve, truth_value)

                # Agréger
                if out_var.aggregation == "Max":
                    aggregated_curve = np.maximum(aggregated_curve, truncated_curve)
                elif out_var.aggregation == "Sum":
                    aggregated_curve = aggregated_curve + truncated_curve

            # Défuzzifier
            results[out_name] = out_var.defuzzify(aggregated_curve)

        return results
