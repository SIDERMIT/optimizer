from collections import defaultdict


class Assignment:

    def __init__(self):
        pass

    @staticmethod
    def get_origin_stop_node_assignment(hyperpaths, labels, Vij, p, vp, spa, spv):
        """
        to distribute trips of all OD pair in each StopNode of the Origin
        :param hyperpaths: Dic[origin: CityNode][destination: CityNode][StopNode] = List[List[ExtendedNodes]].
        Each List[ExtendedNodes] represent a elemental path.
        :param labels: dic[origin: CityNode][destination: CityNode][ExtendedNode] = Label [
        :param Vij: dic[origin: CityNode][destination: CityNode] = vij
        :param p: width [m] of all CityNode
        :return: dic[origin: CityNode][destination: CityNode][Stop: StopNode] = %V_OD
        """

        assignment = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))

        for origin in hyperpaths:
            for destination in hyperpaths[origin]:

                vij = Vij[origin][destination]

                list_stop = []

                # paradero de d = 1
                stop1 = None
                # otro paradero ( su d puede ser o no 1)
                stop2 = None

                print("origin: {}, destination: {}, vij: {:.2f}".format(origin.graph_node.name,
                                                                        destination.graph_node.name, vij))

                # encontramos paradero de d = 1
                for stop in hyperpaths[origin][destination]:
                    if stop.mode.d == 1:
                        if stop1 is None:
                            stop1 = stop
                        else:
                            stop2 = stop
                    else:
                        stop2 = stop

                    print(
                        "\tmode: {}, label: {:.2f}, node: {}".format(stop.mode.name, labels[origin][destination][stop],
                                                                     stop.city_node.graph_node.name))

                # solo tiene una parada
                if stop1 is None or stop2 is None:
                    if stop1 is not None:
                        assignment[origin][destination][stop1] = 100
                        print("\t\tmode {} assignment [%]: {:.2f}".format(stop1.mode.name, 100))
                    else:
                        assignment[origin][destination][stop2] = 100
                        print("\t\tmode {} assignment [%]: {:.2f}".format(stop2.mode.name, 100))
                # existen ambas paradas
                else:
                    # paradero con d = 1 es de etiqueta minima
                    if labels[origin][destination][stop1] <= labels[origin][destination][stop2]:
                        # calculamos caminata de indiferencia
                        d = vp * (labels[origin][destination][stop2] - labels[origin][destination][stop1]) / (spa / spv)

                        # caminata de indiferencia es mayor a la zona de influencia de stop1
                        if d >= p / 2:
                            assignment[origin][destination][stop1] = 100
                            print("\t\tmode {} assignment [%]: {:.2f}".format(stop1.mode.name, 100))

                        # caminata de indiferencia es menor a la zona de influencia de stop1
                        else:

                            # zona de influencia de stop_2
                            zona_stop_2 = p / stop2.mode.d

                            # encontraremos linea de stop 2
                            position = 0
                            # reconoceremos posición de todos los paraderos ubicado a la derecha de stop1
                            for i in range(int(stop2.mode.d / 2)):
                                if i == 0:
                                    position = zona_stop_2 / 2
                                else:
                                    position = position + zona_stop_2
                                # encontramos un paradero de stop2 que esta ubicado mas lejos que la distancia de indiferencia
                                if position > d:
                                    assignment[origin][destination][stop1] = (2 * d + (position - d)) / p * 100
                                    assignment[origin][destination][stop2] = 100 - assignment[origin][destination][
                                        stop1]
                                    print("\t\tmode {} assignment [%]: {:.2f}".format(stop1.mode.name,
                                                                                      assignment[origin][destination][
                                                                                          stop1]))
                                    print("\t\tmode {} assignment [%]: {:.2f}".format(stop2.mode.name,
                                                                                      assignment[origin][destination][
                                                                                          stop2]))
                                    break
                            # si no se encontro paradero mas lejos a la distancia de indiferencia asignar to do a stop1
                            if position < d:
                                assignment[origin][destination][stop1] = 100
                                print("\t\tmode {} assignment [%]: {:.2f}".format(stop1.mode.name, 100))
                    else:
                        # si parametro d de stop2 es impar
                        if stop2.d % 2 == 1:
                            assignment[origin][destination][stop2] = 100
                            print("\t\tmode {} assignment [%]: {:.2f}".format(stop2.mode.name, 100))
                        else:
                            # calculamos caminata de indiferencia
                            d = vp * (labels[origin][destination][stop1] - labels[origin][destination][stop2]) / (
                                        spa / spv)

                            # necesitamos posicion del primer paradero stop2 a la derecha del centro
                            position = (p / stop2.mode.d) * 0.5

                            if d >= position:
                                assignment[origin][destination][stop2] = 100
                                print("\t\tmode {} assignment [%]: {:.2f}".format(stop2.mode.name, 100))
                            else:
                                assignment[origin][destination][stop1] = (position - d) / p * 100
                                assignment[origin][destination][stop2] = 100 - assignment[origin][destination][
                                    stop1]

                                print("\t\tmode {} assignment [%]: {:.2f}".format(stop1.mode.name,
                                                                                  assignment[origin][destination][
                                                                                      stop1]))
                                print("\t\tmode {} assignment [%]: {:.2f}".format(stop2.mode.name,
                                                                                  assignment[origin][destination][
                                                                                      stop2]))
