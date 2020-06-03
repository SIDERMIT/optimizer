import pandas as pd
import numpy as np


# class to build matrix od
class matrixod:
    def __init__(self, n=None,
                 y=None, a=None, alpha=None, beta=None,
                 df_matrix=None):
        self.n = n
        self.y = y
        self.a = a
        self.alpha = alpha
        self.beta = beta

        self.matrix = pd.DataFrame()
        self.plot = False
        self.text = ""

        validation_matrix, text_matrix = self.matrix_validation(df_matrix)
        validation_parameters, text_parameters = self.parameters_validation(n, y, a, alpha, beta)

        if validation_matrix is False and df_matrix is not None:
            self.text = text_matrix
        if validation_parameters is False and df_matrix is None:
            self.text = text_parameters

        # Permitimos demanda asimetrica mediante la carga de un archivo de texto
        # (periferias + subcentros + CBD = 2n+1)
        if validation_matrix:
            self.matrix = df_matrix
            self.plot = True
        # construimos demanda simétrica con los parámetros n, Y, a, aplha y beta
        if validation_parameters:
            np_array = np.zeros((2 * self.n + 1, 2 * self.n + 1))
            self.matrix = pd.DataFrame(np_array)
            nodes = np.arange(0, 2 * self.n + 1, 1)  # inicio, final (excluido), paso

            # asignamos valores a otros parámetros
            b = 1 - self.a
            gamma = 0
            gamma_g = 0
            if self.n > 1:
                gamma = 1 - self.alpha - self.beta
                alpha_g = self.alpha / (1 - self.beta)
                gamma_g = gamma / (1 - self.beta)
            else:
                self.beta = 1 - self.alpha
                alpha_g = 1

            # demanda de la zona
            if self.n != 0:
                y_z = self.y / self.n
            else:
                y_z = y
            # demanda de la periferia
            y_p = self.a * y_z
            # demanda del subcentro
            y_sc = b * y_z
            # viajes periferia - CBD
            v_p_cbd = self.alpha * y_p
            # viajes periferia - subcentro
            v_p_sc = self.beta * y_p
            # viajes periferia - otros sub centros
            v_p_osc = 0
            if n > 1:
                v_p_osc = gamma * y_p / (self.n - 1)
            # viajes subcentro - cbd
            v_sc_cbd = y_sc * alpha_g
            # viajes subcentro -  otros subcentros
            v_sc_osc = 0
            if n > 1:
                v_sc_osc = y_sc * gamma_g / (self.n - 1)
            # nodos que generan viajes
            for row in nodes:
                # nodos que atraen viajes
                for col in nodes:
                    if row == 0:  # generador de viajes es el CBD
                        continue
                    if row % 2 == 0 and row != 0:  # generador de viajes es un SC
                        if col % 2 == 1:  # atracción de viajes es una periferia
                            continue
                        if col == 0:  # atracción de viajes es el CBD
                            self.change_vij(row, col, v_sc_cbd)
                        if col % 2 == 0 and row != col and col != 0:  # atracción de viajes es otro subcentro
                            self.change_vij(row, col, v_sc_osc)
                    if row % 2 == 1:  # generador de viajes es una periferia
                        if col % 2 == 1:  # atracción de viajes es una periferia
                            continue
                        if col == 0:  # atracción de viajes es el CBD
                            self.change_vij(row, col, v_p_cbd)
                        if col == row + 1:  # atraccion de viajes es el propio SC
                            self.change_vij(row, col, v_p_sc)
                        if col % 2 == 0 and col != row + 1 and col != 0:  # atracción de viajes es otro subcentro
                            self.change_vij(row, col, v_p_osc)
            self.plot = True

    # check if dimension of the OD matrix is 2n+1
    @staticmethod
    def check_dimension(n, matrix):
        n_col = len(matrix)
        n_row = len(matrix[0])
        if n_col == 2 * n + 1 and n_row == 2 * n + 1:
            return True
        else:
            return False

    # change vij of the od Matrix
    def change_vij(self, row, col, vij):
        self.matrix[col][row] = vij

    # validamos matriX Od proporcionada externamente
    def matrix_validation(self, df_matrix):
        # leemos texto y reconocemos las dimensiones
        # elementos impares son periferias
        # elementos pares son sub centros
        # elemento 0 es el CBD
        # relación de periferias y sub centro de una misma zona k e [1,...,n] -> periferia = 2k-1, subcentro = 2k
        matrix = df_matrix
        text = ""
        if matrix is None:
            text = "Error matrixod: No data"
            return False, text
        if self.check_dimension(self.n, matrix):
            text = ""
        else:
            text = "Error matrixod: Matriz no cumple con criterio de dimensión de (2n+1)*(2n+1)"
            return False, text
        return True, text

    # validacion de parámetros
    @staticmethod
    def parameters_validation(n, y, a, alpha, beta):

        text = ""

        if n is None:
            text = "Error matrixod: debe especificar valor para n"
            return False, text
        if y is None:
            text = "Error matrixod: debe especificar valor para y"
            return False, text
        if a is None:
            text = "Error matrixod: debe especificar valor para a"
            return False, text
        if alpha is None:
            text = "Error matrixod: debe especificar valor para alpha"
            return False, text
        if beta is None:
            text = "Error matrixod: debe especificar valor para beta"
            return False, text
        if n is not None:
            if n <= 0:
                text = "Error matrixod: n debe ser mayor a 0"
                return False, text
        if y is not None:
            if y <= 0:
                text = "Error matrixod: y debe ser mayor a 0"
                return False, text
        if a is not None:
            if a > 1 or a < 0:
                text  = "Error matrixod: a debe pertenecer a intervalo [0,1]"
                return False, text
        if alpha is not None:
            if alpha > 1 or alpha < 0:
                text = "Error matrixod: alpha debe pertenecer a intervalo [0,1]"
                return False, text
        if beta is not None:
            if beta > 1 or beta < 0:
                text = "Error matrixod: beta debe pertenecer a intervalo [0,1]"
            return False, text
        if alpha is not None and beta is not None:
            if alpha + beta > 1:
                text = "Error matrixod: alpha + beta debe pertenecer a intervalo [0,1]"
                return False, text
        if n is not None and alpha is not None and beta is not None:
            if n == 1 and alpha + beta != 1:
                text = "Warning matrixod: 1 zona, alpha + beta deben sumar 1, se actualiza valor de beta = 1 - alpha"
        return True, text
