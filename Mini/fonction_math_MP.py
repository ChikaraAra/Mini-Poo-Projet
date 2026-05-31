# fonction_math_MP.py
import numpy as np


class Triangulaire:
    """Fonction d'appartenance triangulaire."""

    def __init__(self, a: float, b: float, c: float):
        if not (a <= b <= c) or a == c:
            raise ValueError("Il faut a <= b <= c avec a != c.")
        self.a = a
        self.b = b
        self.c = c

    def __call__(self, x: float) -> float:
        # Montée depuis a jusqu'à b
        if self.a == self.b:
            if x <= self.b:
                return 1.0
        elif self.a < x < self.b:
            return (x - self.a) / (self.b - self.a)

        # Sommet au point b
        if x == self.b:
            return 1.0

        # Descente de b jusqu'à c
        if self.b == self.c:
            if x >= self.b:
                return 1.0
        elif self.b < x < self.c:
            return (self.c - x) / (self.c - self.b)

        return 0.0


class Trapezoidale:
    """Fonction d'appartenance trapézoïdale."""

    def __init__(self, a: float, b: float, c: float, d: float):
        if not (a <= b <= c <= d) or a == d:
            raise ValueError("Les points doivent être ordonnés : a <= b <= c <= d avec a != d.")
        self.a = a
        self.b = b
        self.c = c
        self.d = d

    def __call__(self, x: float) -> float:
        # Plateau central entre b et c
        if self.b <= x <= self.c:
            return 1.0
        # Montée de a vers b
        if self.a < self.b and self.a < x < self.b:
            return (x - self.a) / (self.b - self.a)
        # Descente de c vers d
        if self.c < self.d and self.c < x < self.d:
            return (self.d - x) / (self.d - self.c)
        return 0.0


class DemiTrapezeGauche:
    """Fonction d'appartenance : plateau à 1, puis descente vers 0."""

    def __init__(self, a: float, b: float):
        if not a < b:
            raise ValueError("Il faut a < b.")
        self.a = a
        self.b = b

    def __call__(self, x: float) -> float:
        if x <= self.a:
            return 1.0
        if self.a < x < self.b:
            return (self.b - x) / (self.b - self.a)
        return 0.0


class DemiTrapezeDroite:
    """Fonction d'appartenance : montée vers 1, puis plateau à 1."""

    def __init__(self, a: float, b: float):
        if not a < b:
            raise ValueError("Il faut a < b.")
        self.a = a
        self.b = b

    def __call__(self, x: float) -> float:
        if x <= self.a:
            return 0.0
        if self.a < x < self.b:
            return (x - self.a) / (self.b - self.a)
        return 1.0


class Gaussienne:
    """Fonction d'appartenance gaussienne normalisée."""

    def __init__(self, moyenne: float, ecart_type: float):
        if ecart_type <= 0:
            raise ValueError("L'écart-type doit être positif.")
        self.moyenne = moyenne
        self.ecart_type = ecart_type

    def __call__(self, x: float) -> float:
        return float(np.exp(-0.5 * ((x - self.moyenne) / self.ecart_type) ** 2))
