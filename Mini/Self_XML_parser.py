# Self_XML_parser.py
import xml.etree.ElementTree as ET
from Classes_MP import FuzzySystem, InputVariable, OutputVariable, FuzzySet, Rule


def ChargementXML(chemin_fichier: str) -> FuzzySystem:
    """Charge un fichier XML et construit le système flou."""
    tree = ET.parse(chemin_fichier)
    root = tree.getroot()
    systeme = FuzzySystem()

    # Charger les variables d'entrée
    for _variable in root.find('InputVariables'):
        var = InputVariable(_variable.get('name'),float(_variable.get('min')),float(_variable.get('max')),_variable.get('unit', ''))
        for _ensemble in _variable:
            parametres = {}
            for k, v in _ensemble.attrib.items():
                if k in ('name', 'type'):
                    continue
                # Garder 'left'/'right' en texte, convertir le reste en float
                if k == 'a' and v in ('left', 'right'):
                    parametres[k] = v
                else:
                    parametres[k] = float(v)
            var.add_set(FuzzySet(_ensemble.get('name'), _ensemble.get('type'), parametres))
        
        systeme.inputs[_variable.get('name')] = var

    # Charger les variables de sortie
    for _variable in root.find('OutputVariables'):
        var = OutputVariable(
            _variable.get('name'),
            float(_variable.get('min')),
            float(_variable.get('max')),
            _variable.get('unit', ''),
            int(_variable.get('nb_points', 200)),
            _variable.get('aggregation', 'Max'),
            _variable.get('defuzzification', 'CoG')
        )
        
        # Ajouter les ensembles flous pour cette variable
        for _ensemble in _variable:
            parametres = {}
            for k, v in _ensemble.attrib.items():
                if k in ('name', 'type'):
                    continue
                if k == 'a' and v in ('left', 'right'):
                    parametres[k] = v
                else:
                    parametres[k] = float(v)
            var.add_set(FuzzySet(_ensemble.get('name'), _ensemble.get('type'), parametres))
        
        systeme.outputs[_variable.get('name')] = var

    # Charger les règles de production
    for _regle in root.find('Rules'):
        premise_xml = _regle.find('Premise')
        arbre_premisse = _construire_premisse(premise_xml)
        
        # Récupérer les conclusions de la règle
        conclusions = []
        for _conclusion in _regle.findall('Conclusion'):
            conclusions.append((_conclusion.get('variable'), _conclusion.get('set')))

        systeme.rules.append(Rule(
            _regle.get('id'),
            _regle.get('description', ''),
            arbre_premisse,
            conclusions
        ))

    return systeme


def _construire_premisse(node) -> dict:
    """Convertit un nœud XML en arbre de prémise (structure récursive)."""
    # Cas simple : une clause isolée sur une variable
    if node.tag == 'Clause':
        return {'variable': node.get('variable'), 'set': node.get('set')}

    # Cas composé : un opérateur logique avec enfants
    operateur = node.get('operator', 'AND')
    enfants = [_construire_premisse(child) for child in node]

    # Si un seul enfant, retourner directement (sauf s'il y a un NOT)
    if len(enfants) == 1:
        if operateur == 'NOT':
            return {'operator': 'NOT', 'children': enfants}
        else:
            return enfants[0]

    # Chaîner les enfants deux par deux pour les opérateurs binaires
    resultat = {'operator': operateur, 'children': [enfants[0], enfants[1]]}
    for i in range(2, len(enfants)):
        resultat = {'operator': operateur, 'children': [resultat, enfants[i]]}
    return resultat
