# fuzzy_math.py

import numpy as np

def triangulaire(x, a, b, c):
    """Calcule le degré d'appartenance pour une loi triangle."""
    if x <= a or x >= c:
        return 0
    elif a < x <= b:
        return (x - a) / (b - a) if (b - a) != 0 else 1.0
    elif b < x < c:
        return (c - x) / (c - b) if (c - b) != 0 else 1.0
    return 0

def trapezoidale(x, a, b, c, d):
    """Calcule le degré d'appartenance pour une loi trapèze ou demi-trapèze."""
    if x <= a or x >= d:
        return 0
    elif a < x < b:
        return (x - a) / (b - a) if (b - a) != 0 else 1.0
    elif b <= x <= c:
        return 1
    elif c < x < d:
        return (d - x) / (d - c) if (d - c) != 0 else 1.0
    return 0

def gaussienne(x, moyenne, ecart_type):
    return np.exp(-0.5 * ((x - moyenne) / ecart_type) ** 2)
