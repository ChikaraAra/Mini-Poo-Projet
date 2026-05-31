# Self_XML_parser.py
import xml.etree.ElementTree as ET
from Classes_MP import FuzzySystem, InputVariable, OutputVariable, FuzzySet, Rule


def ChargementXML(chemin_fichier: str) -> FuzzySystem:
    """Charge un fichier XML et retourne un objet FuzzySystem prêt à l'emploi."""
    tree = ET.parse(chemin_fichier)
    root = tree.getroot()

    systeme = FuzzySystem()

    # Récupération des variables d'entrée et de leurs ensembles flous
    for _variable in root.find('InputVariables'):
        var = InputVariable(
            _variable.get('name'),
            float(_variable.get('min')),
            float(_variable.get('max')),
            _variable.get('unit', '')
        )
        for _ensemble in _variable:
            # On récupère les paramètres de l'ensemble flou
            # 'a' peut valoir "left" ou "right" pour le demi-trapèze : on le garde tel quel
            params = {}
            for k, v in _ensemble.attrib.items():
                if k in ('name', 'type'):
                    continue
                if k == 'a' and v in ('left', 'right'):
                    params[k] = v
                else:
                    params[k] = float(v)
            var.add_set(FuzzySet(_ensemble.get('name'), _ensemble.get('type'), params))
        systeme.inputs[_variable.get('name')] = var

    # Récupération des variables de sortie et de leurs ensembles flous
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
        for _ensemble in _variable:
            params = {}
            for k, v in _ensemble.attrib.items():
                if k in ('name', 'type'):
                    continue
                if k == 'a' and v in ('left', 'right'):
                    params[k] = v
                else:
                    params[k] = float(v)
            var.add_set(FuzzySet(_ensemble.get('name'), _ensemble.get('type'), params))
        systeme.outputs[_variable.get('name')] = var

    # Récupération des règles avec leurs prémisses (potentiellement imbriquées)
    for _regle in root.find('Rules'):
        premise_xml = _regle.find('Premise')
        arbre_premisse = _parser_premisse(premise_xml)

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


def _parser_premisse(node) -> dict:
    """Convertit récursivement un nœud XML de prémisse en arbre de conditions (dict)."""
    # Cas feuille : une clause simple sur une variable
    if node.tag == 'Clause':
        return {'variable': node.get('variable'), 'set': node.get('set')}

    # Cas nœud : opérateur logique avec enfants
    operateur = node.get('operator', 'AND')
    enfants = [_parser_premisse(child) for child in node]

    # Prémisse à un seul enfant (clause sans opérateur, ou NOT)
    if len(enfants) == 1:
        if operateur == 'NOT':
            return {'operator': 'NOT', 'children': enfants}
        else:
            # Clause unique sans vrai opérateur : on retourne directement la clause
            return enfants[0]

    # Si plus de 2 enfants (ex: AND de 3 conditions), on les chaîne deux par deux
    resultat = {'operator': operateur, 'children': [enfants[0], enfants[1]]}
    for i in range(2, len(enfants)):
        resultat = {'operator': operateur, 'children': [resultat, enfants[i]]}
    return resultat
