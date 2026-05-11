import tkinter as TK
import xml.etree.ElementTree as ET

def ChargementXML(chemin_fichier):
    tree = ET.parse(chemin_fichier)
    root = tree.getroot()

# Definition des listes de stockage des variables d'entrée et de sortie
    input_variables = []
    output_variables = []

# Recupération des variables d'entrée et de leurs ensembles flous dans des listes
    for _variable in root.find('InputVariables'):
        input_variables.append(_variable)

# Recupération des variables de sortie et de leurs ensembles flous dans des listes
    for _variable in root.find('OutputVariables'):
        # Récupération des paramètres de la variable de sortie
        nom = _variable.get('name')
        borne_inf = _variable.get('min')
        borne_sup = _variable.get('max')
        unite = _variable.get('unit')
        nb_points = _variable.get('nb_points')
        aggregation = _variable.get('aggregation')
        defuzzification = _variable.get('defuzzification')
        
        output_variables.append(_variable)
    
    return(input_variables, output_variables)

print(ChargementXML("problem_1.xml"))