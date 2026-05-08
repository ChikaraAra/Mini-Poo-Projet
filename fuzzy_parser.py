# fuzzy_parser.py
import xml.etree.ElementTree as ET
from Classes_MP import FuzzySystem, InputVariable, OutputVariable, FuzzySet, Rule

def parse_xml(filepath):
    """Parse le fichier XML et retourne un objet FuzzySystem prêt à l'emploi."""
    tree = ET.parse(filepath)
    root = tree.getroot()
    system = FuzzySystem()

    # Lecture des variables d'entrée
    for in_var_node in root.find('InputVariables'):
        var_name = in_var_node.get('name')
        var = InputVariable(
            var_name,
            float(in_var_node.get('min')),
            float(in_var_node.get('max')),
            in_var_node.get('unit', '')
        )
        for set_node in in_var_node:
            params = {k: float(v) for k, v in set_node.attrib.items() if k not in ['name', 'type']}
            var.add_set(FuzzySet(set_node.get('name'), set_node.get('type'), params))
        system.inputs[var_name] = var

    # Lecture des variables de sortie
    for out_var_node in root.find('OutputVariables'):
        var_name = out_var_node.get('name')
        var = OutputVariable(
            var_name,
            float(out_var_node.get('min')),
            float(out_var_node.get('max')),
            out_var_node.get('unit', ''),
            int(out_var_node.get('nb_points', 200)), # Discrétisation par défaut
            out_var_node.get('aggregation', 'Max'),
            out_var_node.get('defuzzification', 'CoG')
        )
        for set_node in out_var_node:
            params = {k: float(v) for k, v in set_node.attrib.items() if k not in ['name', 'type']}
            var.add_set(FuzzySet(set_node.get('name'), set_node.get('type'), params))
        system.outputs[var_name] = var

    # Lecture récursive des règles (Prémisses)
    def parse_premise(node):
        if node.tag == 'Clause':
            return {'variable': node.get('variable'), 'set': node.get('set')}
        else:
            return {
                'operator': node.get('operator', 'NOT' if len(node) == 1 else 'AND'),
                'children': [parse_premise(child) for child in node]
            }

    for rule_node in root.find('Rules'):
        premise_tree = parse_premise(rule_node.find('Premise'))
        conclusions = []
        for concl_node in rule_node.findall('Conclusion'):
            conclusions.append((concl_node.get('variable'), concl_node.get('set')))
            
        system.rules.append(Rule(
            rule_node.get('id'),
            rule_node.get('description'),
            premise_tree,
            conclusions
        ))

    return system