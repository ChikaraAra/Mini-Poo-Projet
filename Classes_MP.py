# fuzzy_classes.py
import numpy as np
from fonction_math_MP import Triangulaire, Trapezoidale, Gaussienne, DemiTrapezeGauche, DemiTrapezeDroite



class FuzzySet:
    """Définit un ensemble flou (ex: 'Froid', 'Chaud') et sa loi mathématique."""
    def __init__(self, name, set_type, params):
        self.name = name
        self.set_type = set_type
        self.params = params

    def get_appartenance(self, x):
        """Étape 1 : Retourne le degré d'appartenance µ pour une valeur x."""
        if self.set_type == "triangulaire":
            return Triangulaire(self.params['a'], self.params['b'], self.params['c'])(x)
        elif self.set_type == "trapezoidale":
            return Trapezoidale(self.params['a'], self.params['a'], self.params['b'], self.params['c'])(x)
        elif self.set_type == "gaussienne":
            return Gaussienne(self.params['moyenne'], self.params['ecart_type'])(x)
        return 0.0

class Variable:
    """Classe parente pour les variables d'entrée et de sortie."""
    def __init__(self, name, min_val, max_val, unit=""):
        self.name = name
        self.min_val = min_val
        self.max_val = max_val
        self.unit = unit
        self.fuzzy_sets = {} # Dictionnaire {nom_ensemble: objet FuzzySet}

    def add_set(self, fuzzy_set):
        self.fuzzy_sets[fuzzy_set.name] = fuzzy_set

class InputVariable(Variable):
    """Paramètre d'entrée réel."""
    def fuzzify(self, value):
        """Calcule le degré d'appartenance de la valeur réelle à tous les ensembles flous."""
        return {name: fset.get_appartenance(value) for name, fset in self.fuzzy_sets.items()}

class OutputVariable(Variable):
    """Paramètre de sortie nécessitant agrégation et défuzzification."""
    def __init__(self, name, val_min, val_max, unité, nb_points, aggregation, defuzzification):
        super().__init__(name, val_min, val_max, unité)
        self.nb_points = int(nb_points)
        self.aggregation = aggregation
        self.defuzzification = defuzzification
        # Discrétisation du domaine de définition pour l'agrégation
        self.x_domain = np.linspace(val_min, val_max, self.nb_points)
    
    def defuzzify(self, courbe):
        """Étape 4 : Concrétisation (CoG ou MoM)."""
        sum_mu = np.sum(courbe)
        if sum_mu == 0:
            return 0.0 # Évite la division par zéro si aucune règle n'est activée
            
        if self.defuzzification == "CoG":
            # Formule du Centre de Gravité
            return np.sum(self.x_domain * courbe) / sum_mu
            
        elif self.defuzzification == "MoM":
            # Moyenne des maximums
            max_val = np.max(courbe)
            indices = np.where(courbe == max_val)[0]
            return np.mean(self.x_domain[indices])

class Rule:
    """Représente une règle floue (Prémisses -> Conclusions)."""
    def __init__(self, rule_id, description, premise_tree, conclusions):
        self.id = rule_id
        self.description = description
        self.premise_tree = premise_tree # Arbre récursif des conditions
        self.conclusions = conclusions   # Liste de tuples (variable_sortie, ensemble_flou)

    def evaluate_premise(self, node, fuzzified_inputs):
        """Étape 2 : Inférence avec évaluation récursive des opérateurs logiques."""
        if 'variable' in node: # C'est une clause finale (feuille)
            return fuzzified_inputs[node['variable']][node['set']]
        
        # C'est un opérateur (nœud)
        op = node['operator']
        
        if op == "NOT":
            return 1.0 - self.evaluate_premise(node['children'][0], fuzzified_inputs)
            
        # Évaluation des enfants pour ET, OU, XOR
        val1 = self.evaluate_premise(node['children'][0], fuzzified_inputs)
        val2 = self.evaluate_premise(node['children'][1], fuzzified_inputs)
        
        if op == "AND":
            return min(val1, val2)
        elif op == "OR":
            return max(val1, val2)
        elif op == "XOR":
            return max(val1, val2) - min(val1, val2)

class FuzzySystem:
    """Le moteur flou principal contenant les variables et les règles."""
    def __init__(self):
        self.inputs = {}
        self.outputs = {}
        self.rules = []

    def compute(self, input_values):
        """Orchestre la résolution complète du problème flou."""
        # 1. Fuzzification
        fuzzified = {}
        for name, var in self.inputs.items():
            fuzzified[name] = var.fuzzify(input_values[name])

        # 2. Inférence des règles
        rule_results = []
        for rule in self.rules:
            truth_value = rule.evaluate_premise(rule.premise_tree, fuzzified)
            if truth_value > 0:
                for out_var, out_set in rule.conclusions:
                    rule_results.append((out_var, out_set, truth_value))

        # 3. Agrégation & 4. Concrétisation (Défuzzification)
        results = {}
        for out_name, out_var in self.outputs.items():
            # Initialisation de la courbe agrégée avec des zéros
            aggregated_curve = np.zeros(out_var.nb_points)
            
            # Récupération de toutes les règles qui modifient cette variable de sortie
            relevant_results = [r for r in rule_results if r[0] == out_name]
            
            for _, set_name, truth_value in relevant_results:
                f_set = out_var.fuzzy_sets[set_name]
                # Calcul de la courbe de l'ensemble flou sur tout le domaine discret
                set_curve = np.array([f_set.get_membership(x) for x in out_var.x_domain])
                
                # Troncation par le degré d'appartenance de la prémisse
                truncated_curve = np.minimum(set_curve, truth_value)
                
                # Agrégation (Max ou Sum)
                if out_var.aggregation == "Max":
                    aggregated_curve = np.maximum(aggregated_curve, truncated_curve)
                elif out_var.aggregation == "Sum":
                    aggregated_curve = aggregated_curve + truncated_curve
                    
            # 4. Défuzzification
            results[out_name] = out_var.defuzzify(aggregated_curve)
            
        return results
