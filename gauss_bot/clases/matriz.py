from copy import deepcopy
from fractions import Fraction
from typing import Union, Optional, overload

Validacion = tuple[bool, int]


class Matriz:
    """
    Representa una matriz matemática de cualquier dimensión.
    Los valores se almacenan una lista bidimensional de objetos Fraction().
    Si la matriz representa un sistema de ecuaciones lineales, se puede indicar que incluye una columna aumentada.
    """

    def __init__(self, aumentada: bool, filas: int, columnas: int, valores: Optional[list[list[Fraction]]] = None) -> None:
        self._aumentada = aumentada
        self._filas = filas
        self._columnas = columnas
        if valores is None:
            self._valores = [[Fraction(0) for _ in range(columnas)] for _ in range(filas)]
        else:
            self._valores = valores

    @property
    def aumentada(self) -> bool:
        return self._aumentada

    @property
    def filas(self) -> int:
        return self._filas

    @property
    def columnas(self) -> int:
        return self._columnas

    @property
    def valores(self) -> list[list[Fraction]]:
        return self._valores

    @overload
    def __getitem__(self, indice: int) -> list[Fraction]: ...

    @overload
    def __getitem__(self, indices: tuple[int, int]) -> Fraction: ...

    def __getitem__(self, indice: Union[int, tuple[int, int]]) -> Union[list[Fraction], Fraction]:
        """
        Overloads para acceder a una fila de la matriz, o a un valor específico.
        """

        if isinstance(indice, int):
            if indice < 0 or indice >= self.filas:
                raise IndexError("Índice inválido!")
            return self.valores[indice]
        if isinstance(indice, tuple) and len(indice) == 2:
            fila, columna = indice
            if fila >= self.filas or columna >= self.columnas:
                raise IndexError("Índice inválido!")
            return self.valores[fila][columna]
        raise TypeError("Índice inválido!")

    def __setitem__(self, indices: tuple[int, int], valor: Fraction) -> None:
        fila, columna = indices
        if fila < 0 or columna < 0 or fila >= self.filas or columna >= self.columnas:
            raise IndexError("Índice inválido!")
        self.valores[fila][columna] = valor

    def __eq__(self, mat2: object) -> bool:
        if not isinstance(mat2, Matriz):
            return False
        if self.filas != mat2.filas or self.columnas != mat2.columnas:
            return False
        return all(
            a == b
            for fila1, fila2 in zip(self.valores, mat2.valores)
            for a, b in zip(fila1, fila2)
        )

    def __str__(self) -> str:
        """
        Para poder imprimir matrices con sus elementos centrados y alineados.
        """

        max_len = max(
            len(str(self.valores[i][j].limit_denominator(100)))
            for i in range(self.filas)
            for j in range(self.columnas)
        )

        matriz = ""
        for i in range(self.filas):
            for j in range(self.columnas):
                valor = str(self.valores[i][j].limit_denominator(100)).center(max_len)
                if j == 0 and j == self.columnas - 1:
                    matriz += f"( {valor} )"
                elif j == 0:
                    matriz += f"( {valor}, "
                elif j == self.columnas - 2 and self.aumentada:
                    matriz += f"{valor} | "
                elif j == self.columnas - 1:
                    matriz += f"{valor} )"
                else:
                    matriz += f"{valor}, "
            matriz += "\n"
        return matriz

    def __add__(self, mat2: "Matriz") -> "Matriz":
        if self.filas != mat2.filas or self.columnas != mat2.columnas:
            raise ArithmeticError("Las matrices deben tener las mismas dimensiones!")
        mat_sumada = [
            [a + b for a, b in zip(filas1, filas2)]
            for filas1, filas2 in zip(self.valores, mat2.valores)
        ]

        return Matriz(self.aumentada, self.filas, self.columnas, mat_sumada)

    def __sub__(self, mat2: "Matriz") -> "Matriz":
        if self.filas != mat2.filas or self.columnas != mat2.columnas:
            raise ArithmeticError("Las matrices deben tener las mismas dimensiones!")
        mat_restada = [
            [a - b for a, b in zip(filas1, filas2)]
            for filas1, filas2 in zip(self.valores, mat2.valores)
        ]

        return Matriz(self.aumentada, self.filas, self.columnas, mat_restada)

    @overload
    def __mul__(self, mat2: "Matriz") -> "Matriz": ...

    @overload
    def __mul__(self, escalar: Fraction) -> "Matriz": ...

    def __mul__(self, multiplicador: Union["Matriz", Fraction]) -> "Matriz":
        if isinstance(multiplicador, Matriz):
            if self.columnas != multiplicador.filas:
                raise ArithmeticError("El número de columnas de la primera matriz debe ser igual al número de filas de la segunda matriz!")

            mat_multiplicada = [
                [Fraction(0) for _ in range(multiplicador.columnas)]
                for _ in range(self.filas)
            ]

            for i in range(self.filas):
                for j in range(multiplicador.columnas):
                    for k in range(self.columnas):
                        mat_multiplicada[i][j] += self.valores[i][k] * multiplicador.valores[k][j]

            return Matriz(self.aumentada, self.filas, multiplicador.columnas, mat_multiplicada)
        if isinstance(multiplicador, Fraction):
            mat_multiplicada = [[multiplicador * valor for valor in fila] for fila in self.valores]
            return Matriz(self.aumentada, self.filas, self.columnas, mat_multiplicada)
        raise TypeError("Tipo de dato inválido!")

    def es_matriz_cero(self) -> bool:
        """
        Verifica si todos los valores de la instancia son 0.
        """

        return all(all(x == Fraction(0) for x in fila) for fila in self.valores)

    def es_cuadrada(self) -> bool:
        """
        Verifica si la instancia es una matriz cuadrada.
        """

        return self.filas == self.columnas

    def es_identidad(self) -> bool:
        """
        Verifica si la instancia representa una matriz identidad:
        * Debe ser cuadrada
        * Todos los elementos de la diagonal principal deben ser 1
        * Todos los demás elementos deben ser 0
        """

        diagonales_son_1 = all(self.valores[i][i] == Fraction(1) for i in range(self.filas))
        resto_son_cero = all(self.valores[i][j] == Fraction(0) for i in range(self.filas) for j in range(self.columnas) if i != j)
        return self.es_cuadrada() and diagonales_son_1 and resto_son_cero

    def transponer(self) -> "Matriz":
        """
        Crea una nueva lista bidimensional con los valores de la instancia transpuestos,
        y la retorna como un nuevo objeto Matriz()
        """

        mat_transpuesta = [[self.valores[j][i] for j in range(self.filas)] for i in range(self.columnas)]
        return Matriz(self.aumentada, self.columnas, self.filas, mat_transpuesta)

    def hacer_triangular_superior(self) -> tuple["Matriz", bool]:
        """
        Usada para calcular determinantes. Realiza operaciones de fila
        para convertir la matriz en una matriz triangular superior.
        Retorna un nuevo objeto Matriz() con los valores modificados,
        y un booleano que indica si hubo intercambio de filas.
        """

        intercambio = False
        mat_triangular = deepcopy(self.valores)

        for i in range(self.filas):
            max_f = max(range(i, self.filas), key=lambda j, i=i: abs(mat_triangular[j][i]))  # type: ignore
            if mat_triangular[max_f][i] == 0:
                continue

            if max_f != i:
                mat_triangular[i], mat_triangular[max_f] = mat_triangular[max_f], mat_triangular[i]
                intercambio = not intercambio

            for j in range(i + 1, self.filas):
                factor = mat_triangular[j][i] / mat_triangular[i][i]
                for k in range(self.columnas):
                    mat_triangular[j][k] -= factor * mat_triangular[i][k]

        return (Matriz(self.aumentada, self.filas, self.columnas, mat_triangular), intercambio)
