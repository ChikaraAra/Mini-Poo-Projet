import tkinter as TK
import xml.etree.ElementTree as ET

def ChargementXML(chemin_fichier):
    tree = ET.parse(chemin_fichier)
    root = tree.getroot()

# Definition des listes de stockage des variables d'entrée et de sortie
    input_variables = {}
    output_variables = {}
    rules = {}

# Recupération des variables d'entrée et de leurs ensembles flous dans des listes
    for _variable in root.find('InputVariables'):
        input_variables[_variable.get('name')] = _variable.get('unit')
        for _ensemble in _variable:
            input_variables[_variable.get('name') + '_' + _ensemble.get('name')] = {
                'type': _ensemble.get('type'),
                'params': {k: v for k, v in _ensemble.attrib.items() if k not in ['name', 'type']}
            }

# Recupération des variables de sortie et de leurs ensembles flous dans des listes
    for _variable in root.find('OutputVariables'):
        # Récupération des paramètres de la variable de sortie
        output_variables[_variable.get('name')] = {
            'unit': _variable.get('unit'),
            'min': float(_variable.get('min')),
            'max': float(_variable.get('max')), 
            'nb_points': int(_variable.get('nb_points')),
            'aggregation': _variable.get('aggregation'),
            'defuzzification': _variable.get('defuzzification')
        }

#Récupération des regles
    for _variable in root.find('Rules'):
        rules[_variable.get('id')] = {
            'description': _variable.get('description'),
            'operator': _variable.find('Premise').get('operator'),
            'conditions': [(clause.get('variable'), clause.get('set')) for clause in _variable.find('Premise').findall('Clause')],
            'conclusions': [(concl.get('variable'), concl.get('set')) for concl in _variable.findall('Conclusion')]
        }

    return(input_variables, output_variables, rules)

print(ChargementXML("problem_pourboire.xml")[2])