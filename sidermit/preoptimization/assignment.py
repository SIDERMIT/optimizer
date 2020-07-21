from collections import defaultdict

from sidermit.preoptimization import StopNode, RouteNode


class Assignment:

    def __init__(self):
        pass

    @staticmethod
    def get_assignment(hyperpaths, labels, p, vp, spa, spv):
        """
        to distribute trips of all OD pair in each StopNode of the Origin
        :param vp: Walking speed [km/h]
        :param spv: Subjetive value of in-vehicle time savings [US$/h]
        :param spa: Subjetive value of access time savings [US$/h]
        :param hyperpaths: Dic[origin: CityNode][destination: CityNode][StopNode] = List[List[ExtendedNodes]].
        Each List[ExtendedNodes] represent a elemental path.
        :param labels: dic[origin: CityNode][destination: CityNode][ExtendedNode] = Label [
        :param p: width [m] of all CityNode
        :return: dic[origin: CityNode][destination: CityNode][Stop: StopNode] = %V_OD
        """

        assignment = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))

        for origin in hyperpaths:
            for destination in hyperpaths[origin]:

                # paradero de d = 1
                stop1 = None
                # otro paradero ( su d puede ser o no 1)
                stop2 = None

                # print("origin: {}, destination: {}, vij: {:.2f}".format(origin.graph_node.name,
                #                                                         destination.graph_node.name, vij))

                # encontramos paradero de d = 1
                for stop in hyperpaths[origin][destination]:
                    if stop.mode.d == 1:
                        if stop1 is None:
                            stop1 = stop
                        else:
                            stop2 = stop
                    else:
                        stop2 = stop

                    # print( "\tmode: {}, label: {:.2f}, node: {}".format(stop.mode.name, labels[origin][
                    # destination][stop], stop.city_node.graph_node.name))

                # solo tiene una parada
                if stop1 is None or stop2 is None:
                    if stop1 is not None:
                        assignment[origin][destination][stop1] = 100
                        # print("\t\tmode {} assignment [%]: {:.2f}".format(stop1.mode.name, 100))
                    if stop2 is not None:
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
                                # encontramos un paradero de stop2 que esta ubicado mas lejos que la distancia de
                                # indiferencia
                                if position > d:
                                    assignment[origin][destination][stop1] = (2 * d + (position - d)) / p * 100
                                    assignment[origin][destination][stop2] = 100 - assignment[origin][destination][
                                        stop1]
                                    # print("\t\tmode {} assignment [%]: {:.2f}".format(stop1.mode.name,
                                    #                                                   assignment[origin][destination][
                                    #                                                       stop1]))
                                    # print("\t\tmode {} assignment [%]: {:.2f}".format(stop2.mode.name,
                                    #                                                   assignment[origin][destination][
                                    #                                                       stop2]))
                                    break
                            # si no se encontro paradero mas lejos a la distancia de indiferencia asignar to do a stop1
                            if position < d:
                                assignment[origin][destination][stop1] = 100
                                # print("\t\tmode {} assignment [%]: {:.2f}".format(stop1.mode.name, 100))
                    else:
                        # si parametro d de stop2 es impar
                        if stop2.mode.d % 2 == 1:
                            assignment[origin][destination][stop2] = 100
                            # print("\t\tmode {} assignment [%]: {:.2f}".format(stop2.mode.name, 100))
                        else:
                            # calculamos caminata de indiferencia
                            d = vp * (labels[origin][destination][stop1] - labels[origin][destination][stop2]) / (
                                    spa / spv)

                            # necesitamos posicion del primer paradero stop2 a la derecha del centro
                            position = (p / stop2.mode.d) * 0.5

                            if d >= position:
                                assignment[origin][destination][stop2] = 100
                                # print("\t\tmode {} assignment [%]: {:.2f}".format(stop2.mode.name, 100))
                            else:
                                assignment[origin][destination][stop1] = (position - d) / p * 100
                                assignment[origin][destination][stop2] = 100 - assignment[origin][destination][
                                    stop1]

                                # print("\t\tmode {} assignment [%]: {:.2f}".format(stop1.mode.name,
                                #                                                   assignment[origin][destination][
                                #                                                       stop1]))
                                # print("\t\tmode {} assignment [%]: {:.2f}".format(stop2.mode.name,
                                #                                                   assignment[origin][destination][
                                #                                                       stop2]))
        return assignment

    @staticmethod
    def get_alighting_and_boarding(Vij, hyperpaths, successors, assignment, f):
        """
        to get two matrix (z and v) with alighting and boarding for vehicle in each stop of all routes :param
        successors: dic[origin: CityNode][destination: CityNode] [ExtendedNode] = List[ExtendedEdge],
        List[ExtendedEdge] represent all successors edge for each ExtendedNode in a OD pair. :param frequencies: dic[
        origin: CityNode][destination: CityNode][ExtendedNode] = float [veh/hr]. :param Vij: dic[origin: CityNode][
        destination: CityNode] = vij [pax/hr] :param hyperpaths: Dic[origin: CityNode][destination: CityNode][
        StopNode] = List[List[ExtendedNodes]]. Each List[ExtendedNodes] represent a elemental path to connect a
        origin and destination :param assignment: dic[origin: CityNode][destination: CityNode][Stop: StopNode] =
        %V_OD :param f: dic[route_id] = frequency [veh/hr] :return: dic[route_id][direction][stop: StopNode] = pax [
        pax/veh], dic[route_id][direction][stop: StopNode] = pax [pax/veh]
        """

        z = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
        v = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))

        for origin in hyperpaths:
            for destination in hyperpaths[origin]:
                # viajes del par OD
                vod = Vij[origin][destination]
                for stop in hyperpaths[origin][destination]:
                    # viajes de todas las rutas elementales que salen de esta parada
                    vod_s = vod * assignment[origin][destination][stop] / 100

                    if vod_s == 0:
                        continue

                    paths = []

                    for suc in successors[origin][destination][stop]:
                        nodej = suc.nodej
                        paths.append((stop, nodej, vod_s))

                    while len(paths) != 0:
                        nodei, nodej, pax = paths.pop(0)

                        dis_pax = pax

                        if isinstance(nodei, StopNode):
                            # reportar subidas
                            if isinstance(nodej, RouteNode):

                                f_acum = 0

                                for suc in successors[origin][destination][nodei]:
                                    f_acum += f[suc.nodej.route.id]

                                dis_pax = pax * (f[nodej.route.id] / f_acum)

                                z[nodej.route.id][nodej.direction][nodei] += dis_pax

                        if isinstance(nodei, RouteNode):
                            # reportar bajadas
                            if isinstance(nodej, StopNode):
                                v[nodei.route.id][nodei.direction][nodej] += dis_pax

                        # agregar nuevos elementos a paths, salvo que hayan llegado a destino
                        if isinstance(nodej, StopNode) and nodej.city_node == destination:
                            continue

                        else:
                            for suc in successors[origin][destination][nodej]:
                                paths.append((nodej, suc.nodej, dis_pax))

        for route_id in z:
            for direction in z[route_id]:
                for stop_node in z[route_id][direction]:
                    if f[route_id] == 0:
                        continue
                    else:
                        z[route_id][direction][stop_node] = z[route_id][direction][stop_node] / (
                                f[route_id] * stop_node.mode.d)
        for route_id in v:
            for direction in v[route_id]:
                for stop_node in v[route_id][direction]:
                    if f[route_id] == 0:
                        continue
                    else:
                        v[route_id][direction][stop_node] = v[route_id][direction][stop_node] / (
                                f[route_id] * stop_node.mode.d)

        return z, v

    @staticmethod
    def str_boarding_alighting(z, v):
        """
        to print boarding and alighting
        :param z:
        :param v:
        :return:
        """
        line = "\nBoarding and Alighting information:"
        for route_id in z:
            line += "\nNew route: {}".format(route_id)
            line += "\n\tBoarding:"
            for direction in z[route_id]:
                line += "\n\t\tDirection: {}".format(direction)
                for stop_node in z[route_id][direction]:
                    line += "\n\t\t\tStop {}-{}: {:.2f}[pax/veh]".format(stop_node.mode.name,
                                                                         stop_node.city_node.graph_node.name,
                                                                         z[route_id][direction][stop_node])
            line += "\n\tAlighting:"
            for direction in v[route_id]:
                line += "\n\t\tDirection: {}".format(direction)
                for stop_node in v[route_id][direction]:
                    line += "\n\t\t\tStop {}-{}: {:.2f}[pax/veh]".format(stop_node.mode.name,
                                                                         stop_node.city_node.graph_node.name,
                                                                         v[route_id][direction][stop_node])
        return line
