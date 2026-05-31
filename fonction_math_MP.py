# fuzzy_math.py

import numpy as np

class Triangulaire:
    """Loi triangulaire définie par trois points a, b, c."""

    def __init__(self, a: float, b: float, c: float):
        if not a < b < c:
            raise ValueError("Il faut a < b < c.")

        self.a = a
        self.b = b
        self.c = c

    def __call__(self, x: float) -> float:

        if x == self.b:
            return 1
        if self.a < x < self.b:
            return (x - self.a) / (self.b - self.a)
        if self.b < x < self.c:
            return (self.c - x) / (self.c - self.b)

        return 0


class Trapezoidale:
    """Loi trapézoïdale définie par quatre points a, b, c, d."""

    def __init__(self, a: float, b: float, c: float, d: float):
        if not a < b <= c < d:
            raise ValueError("Il faut a < b <= c < d")
        self.a = a
        self.b = b
        self.c = c
        self.d = d

    def __call__(self, x: float) -> float:
        
        if self.b <= x <= self.c:
            return 1
        if self.a < x < self.b:
            return (x - self.a) / (self.b - self.a)
        if self.c < x < self.d:
            return (self.d - x) / (self.d - self.c)
        return 0


class DemiTrapezeGauche:
    """Demi-trapèze gauche : plateau à 1 à gauche, puis descente vers 0"""

    def __init__(self, a: float, b: float):
        if not a < b:
            raise ValueError("Il faut a < b.")
        self.a = a
        self.b = b

    def __call__(self, x: float) -> float:
        if x <= self.a:
            return 1
        if self.a < x < self.b:
            return (self.b - x) / (self.b - self.a)
        return 0


class DemiTrapezeDroite:
    """Demi-trapèze droit : montée vers 1, puis plateau à 1 à droite"""

    def __init__(self, a: float, b: float):
        if not a < b:
            raise ValueError("Il faut a < b")
        self.a = a
        self.b = b

    def __call__(self, x: float) -> float:
        if x <= self.a:
            return 0
        if self.a < x < self.b:
            return (x - self.a) / (self.b - self.a)
        return 1


class Gaussienne:
    """Loi gaussienne définie par une moyenne et un écart-type."""

    def __init__(self, moyenne: float, ecart_type: float):
        if ecart_type <= 0:
            raise ValueError("L'écart-type doit être strictement positif.")
        self.moyenne = moyenne
        self.ecart_type = ecart_type

    def __call__(self, x: float) -> float:
        return float(np.exp(-0.5 * ((x - self.moyenne) / self.ecart_type) ** 2))
