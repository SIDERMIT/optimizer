import math
import pandas as pd
import numpy as np


# cosas por hacer: incorporar verificacion de largo de inputs y numero de zonas
# incorporar creación de grafo a partir de csv file
# crearemos grafo de la ciudad parametrizada
class city_graph:

    # n = numero de zonas
    # L distancia entre subcentro (SC) y coordenada (0,0)
    # g*L distancia entre periferia (P) y coordenada (0,0)
    # etha e [0,1] proporción de desplazamiento del CBD con respecto a un SC
    # etha_zone zona con respecto a la cual el CBd se desplaza
    # ang vector de angulo de cada zona con respecto a eje x+ (deben ser menor a 360)
    # Gi vector de alteración de distancia entre SC y (0,0) para cada zona
    # Hi vector de alteracion de distancia entre P y (0,0) para cada zona
    # name_zones nombre de zonas, la zona 0 es el CBD
    # df_edges and df_nodes es un dataframe con la información de arcos y nodos
    def __init__(self, n=None, L=None, g=None, p=None,
                 etha=None, etha_zone=None,
                 angles=None,
                 Gi=None, Hi=None,
                 name_zones=None,
                 df_nodes=None, df_edges=None):

        # return por defaults
        self.nodes = pd.DataFrame()
        self.edges = pd.DataFrame()
        self.plot = False
        self.text = ""

        # Validación de parámetros
        # faltan validaciones geométricas
        validation_parameters, text_parameters = self.parameters_validation(n, L, g, p, etha, etha_zone, angles, Gi,
                                                                                 Hi, name_zones)
        # falta validacion de dataframes de entradas
        validation_nodes, text_nodes = self.nodes_validation(df_nodes)
        validation_edges, text_edges = self.edges_validation(df_edges)

        # Contruccion por archivos externos
        if df_nodes is not None and df_edges is not None and validation_nodes and validation_edges:
            self.nodes = df_nodes
            self.edges = df_edges
            self.plot = True
        if df_nodes is not None and df_edges is not None and validation_nodes is False:
            self.text = text_nodes
        if df_nodes is not None and df_edges is not None and validation_edges is False:
            self.text = text_edges
        # contruccion por parámetros
        # requiere validación de parámetros
        if df_nodes is None and df_edges is None and validation_parameters is False:
            self.text = text_parameters
        if df_nodes is None and df_edges is None and validation_parameters:
            # datos de nodos
            id_nodes = []
            tipo = []
            zones = []
            name = []
            radio = []
            angulo = []
            x = []
            y = []
            # contruimos caso simétrico como base
            if (L is not None and g is not None) and n > 0:  # error
                print("Contruyendo ciudad simétrica con {} zonas".format(n))
                id_nodes.append(0)
                tipo.append("CBD")
                zones.append(0)
                if name_zones is not None:
                    name.append(name_zones[0])
                else:
                    name.append("CBD")
                radio.append(0)
                angulo.append(0)
                x.append(0)
                y.append(0)

                for zone in range(n):
                    id_nodes.append(2 * zone + 1)  # periferia de la zona
                    id_nodes.append(2 * zone + 2)  # Sc de la zona
                    tipo.append("P")
                    tipo.append("SC")
                    zones.append(zone + 1)
                    zones.append(zone + 1)
                    if name_zones is not None:
                        name.append(name_zones[zone + 1])
                        name.append(name_zones[zone + 1])
                    else:
                        name.append("P_{}".format(zone + 1))
                        name.append("SC_{}".format(zone + 1))
                    radio.append(L + g * L)
                    radio.append(L)
                    angulo.append(360 / n * zone)
                    angulo.append(360 / n * zone)
                    x_p, y_p = self.obtain_xy(L + g * L, 360 / n * zone)
                    x_sc, y_sc = self.obtain_xy(L, 360 / n * zone)
                    x.append(x_p)
                    x.append(x_sc)
                    y.append(y_p)
                    y.append(y_sc)

            self.nodes = pd.DataFrame()
            self.nodes["id_nodes"] = id_nodes
            self.nodes["name"] = name
            self.nodes["zone"] = zones
            self.nodes["tipo"] = tipo
            self.nodes["radio"] = radio
            self.nodes["angle"] = angulo
            self.nodes["x"] = x
            self.nodes["y"] = y

            # caso asimetrico por ángulo
            if angles is not None:
                print("Incorporando asimetrías por ángulo")
                z = 1
                for ang in angles:
                    if ang > 360 or ang < 0:
                        # print("Warning city_graph: ángulos deben ser entre [0,360]")
                        z = z + 1
                    else:
                        info = self.nodes[self.nodes["zone"] == z]
                        info_sc = info[info["tipo"] == "SC"]
                        info_p = info[info["tipo"] == "P"]

                        r_sc = info_sc["radio"]
                        r_p = info_p["radio"]

                        x_sc, y_sc = self.obtain_xy(r_sc, ang)
                        x_p, y_p = self.obtain_xy(r_p, ang)

                        # cambiamos datos P
                        self.nodes.at[2 * (z - 1) + 1, 'angle'] = ang
                        self.nodes.at[2 * (z - 1) + 1, 'x'] = x_p
                        self.nodes.at[2 * (z - 1) + 1, 'y'] = y_p
                        # cambiamos datos SC
                        self.nodes.at[2 * (z - 1) + 2, 'angle'] = ang
                        self.nodes.at[2 * (z - 1) + 2, 'x'] = x_sc
                        self.nodes.at[2 * (z - 1) + 2, 'y'] = y_sc

                        z = z + 1

            # asimetría por distancia
            if Gi is not None or Hi is not None:
                print("Incorporando asimetrías por distancia")
                if Hi is None:
                    Hi = np.ones(n)
                if Gi is None:
                    Gi = np.ones(n)
                z = 1
                # cambia coordenadas de SC
                for G in Gi:
                    info = self.nodes[self.nodes["zone"] == z]
                    info_sc = info[info["tipo"] == "SC"]

                    r_sc = info_sc["radio"]
                    ang = info_sc["angle"]
                    # actualizamos radio
                    r_sc = G * r_sc
                    # actualizamos x, y
                    x_sc, y_sc = self.obtain_xy(r_sc, ang)
                    # cambiamos datos SC
                    self.nodes.at[2 * (z - 1) + 2, 'radio'] = r_sc
                    self.nodes.at[2 * (z - 1) + 2, 'x'] = x_sc
                    self.nodes.at[2 * (z - 1) + 2, 'y'] = y_sc

                    z = z + 1

                z = 1
                # cambia coordenadas de SC
                for H in Hi:
                    info = self.nodes[self.nodes["zone"] == z]
                    info_p = info[info["tipo"] == "P"]

                    r_p = info_p["radio"]
                    ang = info_p["angle"]
                    # actualizamos radio
                    r_p = H * r_p
                    # actualizamos x, y
                    x_p, y_p = self.obtain_xy(r_p, ang)
                    # cambiamos datos SC
                    self.nodes.at[2 * (z - 1) + 1, 'radio'] = r_p
                    self.nodes.at[2 * (z - 1) + 1, 'x'] = x_p
                    self.nodes.at[2 * (z - 1) + 1, 'y'] = y_p

                    z = z + 1
            # asimetría por excentricidad debe ser aplicada despues de asimetria por angulo y distancia
            # para que esta vaya en la direccion y en proporcion de distancia adecuada
            # caso asimetrico por excentricidad
            # if etha is not None and etha_zone is None:
            #     print("Warning city_graph: Debe especificar etha_zone")
            # if etha is None and etha_zone is not None:
            #     print("Warning city_graph: Debe especificar etha")
            # if etha == 1 and etha_zone is not None:
            #     print("Warning city_graph: zona {} P, Sc, CBD se sobreponen".format(etha_zone))
            if etha is not None and etha_zone is not None:
                print("Incorporando asimetrías por excentricidad")
                info = self.nodes[self.nodes["zone"] == etha_zone]
                info = info[info["tipo"] == "SC"]
                L_sc = info["radio"]
                ang_sc = info["angle"]
                x_cbd, y_cbd = self.obtain_xy(L_sc * etha, ang_sc)

                self.nodes.at[0, 'radio'] = L_sc * etha
                self.nodes.at[0, 'angle'] = ang_sc
                self.nodes.at[0, 'x'] = x_cbd
                self.nodes.at[0, 'y'] = y_cbd

            # creamos arcos
            # sacamos info del CBD
            x_cbd = self.nodes.at[0, 'x']
            y_cbd = self.nodes.at[0, 'y']

            self.edges = pd.DataFrame()
            id_edges = []
            nodei = []
            nodej = []
            distance = []
            x_i = []
            y_i = []
            x_j = []
            y_j = []
            # para cada zona
            for i in range(n):

                x_p1 = self.nodes.at[2 * i + 1, 'x']
                x_sc1 = self.nodes.at[2 * i + 2, 'x']
                if i == n - 1:
                    x_sc2 = self.nodes.at[2, 'x']
                else:
                    x_sc2 = self.nodes.at[2 * (i + 1) + 2, 'x']

                y_p1 = self.nodes.at[2 * i + 1, 'y']
                y_sc1 = self.nodes.at[2 * i + 2, 'y']
                if i == n - 1:
                    y_sc2 = self.nodes.at[2, 'y']
                else:
                    y_sc2 = self.nodes.at[2 * (i + 1) + 2, 'y']

                dist_p1_sc1 = math.sqrt((x_p1 - x_sc1) ** 2 + (y_p1 - y_sc1) ** 2)
                dist_sc1_cbd = math.sqrt((x_cbd - x_sc1) ** 2 + (y_cbd - y_sc1) ** 2)
                dist_sc1_sc2 = math.sqrt((x_sc2 - x_sc1) ** 2 + (y_sc2 - y_sc1) ** 2)

                id_edges.append(6 * i + 1)  # p - sc1
                id_edges.append(6 * i + 2)  # sc1 - p
                id_edges.append(6 * i + 3)  # sc1 - cbd
                id_edges.append(6 * i + 4)  # cbd - sc1
                id_edges.append(6 * i + 5)  # sc1 - sc2
                id_edges.append(6 * i + 6)  # sc2 - sc1

                nodei.append(2 * i + 1)
                nodei.append(2 * i + 2)
                nodei.append(2 * i + 2)
                nodei.append(0)
                nodei.append(2 * i + 2)
                if i == n - 1:
                    nodei.append(2)
                else:
                    nodei.append(2 * (i + 1) + 2)

                nodej.append(2 * i + 2)
                nodej.append(2 * i + 1)
                nodej.append(0)
                nodej.append(2 * i + 2)
                if i == n - 1:
                    nodej.append(2)
                else:
                    nodej.append(2 * (i + 1) + 2)
                nodej.append(2 * i + 2)

                distance.append(dist_p1_sc1)
                distance.append(dist_p1_sc1)
                distance.append(dist_sc1_cbd)
                distance.append(dist_sc1_cbd)
                distance.append(dist_sc1_sc2)
                distance.append(dist_sc1_sc2)

                x_i.append(x_p1)
                x_i.append(x_sc1)
                x_i.append(x_sc1)
                x_i.append(x_cbd)
                x_i.append(x_sc1)
                x_i.append(x_sc2)

                y_i.append(y_p1)
                y_i.append(y_sc1)
                y_i.append(y_sc1)
                y_i.append(y_cbd)
                y_i.append(y_sc1)
                y_i.append(y_sc2)

                x_j.append(x_sc1)
                x_j.append(x_p1)
                x_j.append(x_cbd)
                x_j.append(x_sc1)
                x_j.append(x_sc2)
                x_j.append(x_sc1)

                y_j.append(y_sc1)
                y_j.append(y_p1)
                y_j.append(y_cbd)
                y_j.append(y_sc1)
                y_j.append(y_sc2)
                y_j.append(y_sc1)

            self.edges["id_edges"] = id_edges
            self.edges["nodei"] = nodei
            self.edges["nodej"] = nodej
            self.edges["distance"] = distance
            self.edges["x_i"] = x_i
            self.edges["y_i"] = y_i
            self.edges["x_j"] = x_j
            self.edges["y_j"] = y_j

            self.plot = True

    # obtenemos coordenada x a partir de coordenadas polares y angulo sexagesimal
    @staticmethod
    def obtain_xy(radio, angle):
        return radio * math.cos(math.radians(angle)), radio * math.sin(math.radians(angle))

    # permite evaluar dataframe de nodes
    @staticmethod
    def nodes_validation(df_nodes):
        text = ""
        if df_nodes is None:
            text = "Error city_graph: proporcionar información de nodos"
            return False, text
        return True, text

    @staticmethod
    def edges_validation(df_edges):
        text = ""
        if df_edges is None:
            text = "Error city_graph: proporcionar información de nodos"
            return False, text
        return True, text

    # permite validad los parámetros de inicialización de la clase
    @staticmethod
    def parameters_validation(n, L, g, p,
                              etha, etha_zone, angles, Gi, Hi,
                              name_zones):
        # para caso simétrico y asimétrico
        if n is None:
            text = "Error city_graph: debe especificar valor para n"
            return False, text
        if n is not None:
            if n <= 0:
                text = "Error city_graph: n debe ser mayor a 0"
                return False, text
        if p is None:
            text = "Error city_graph: debe especificar valor para p"
            return False, text
        if p is not None:
            if p <= 0:
                text = "Error city_graph: p debe ser mayor a 0"
                return False, text
        if L is None:
            text = "Error city_graph: debe especificar valor para L"
            return False, text
        if g is None:
            text = "Error city_graph: debe especificar valor para g"
            return False, text
        if L is not None:
            if L < 0:
                text = "Error city_graph: L debe ser un valor positivo"
                return False, text
        if g is not None:
            if g < 0:
                text = "Error city_graph: g debe ser un valor positivo"
                return False, text
        if name_zones is not None:
            if n != len(name_zones):
                text = "Error city_graph: n_zones debe ser de tamaño n"
                return False, text
        # caso simétrico
        if etha is None and etha_zone is None and angles is None and Gi is None and Hi is None:
            text = ""
        # caso asimétrico
        else:
            text = ""
            # excentricidad
            if etha is None and etha_zone is not None:
                text = "Error city_graph: debe especificar valor para etha y etha_zone simultaneamente"
                return False, text
            if etha is not None and etha_zone is None:
                text = "Error city_graph: debe especificar valor para etha y etha_zone simultaneamente"
                return False, text
            if etha_zone is not None:
                if etha_zone > n or etha_zone < 1:
                    text = "Error city_graph: etha_zone debe ser una zona válida rango en [1,...,n]"
                    return False, text
            if etha is not None:
                if etha > 1 or etha < 0:
                    text = "Error city_graph: etha debe pertenecer a rango [0-1]"
                    return False, text
            if etha == 1 and etha_zone is not None:
                text = "Warning city_graph: zona {}: SC y CBD se sobreponen".format(etha_zone)
            # angularidad
            if angles is not None:
                if n != len(angles):
                    text = "Error city_graph: el vector angles debe ser de tamaño n"
                    return False, text
                for ang in angles:
                    if ang < 0 or ang > 360:
                        text = "Error city_graph: cada angulo de angles debe estar en el rango [0°-360°]"
                        return False, text
            # distancia
            if Gi is not None:
                if n != len(Gi):
                    text = "Error city_graph: Gi debe ser de tamaño n"
                    return False, text
                for gi in Gi:
                    if gi < 0:
                        text = "Error city_graph: cada elemento de Gi debe ser positivo"
                        return False, text
            if Hi is not None:
                if n != len(Hi):
                    text = "Error city_graph: Hi debe ser de tamaño n"
                    return False, text
                for hi in Hi:
                    if hi < 0:
                        text = "Error city_graph: cada elemento de Hi debe ser positivo"
                        return False, text
        return True, text
