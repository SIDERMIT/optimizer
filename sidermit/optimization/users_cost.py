from collections import defaultdict
from typing import List

from sidermit.optimization.preoptimization import RouteNode, StopNode, ExtendedGraph, CityNode, ExtendedEdge, \
    ExtendedNode
from sidermit.publictransportsystem import Passenger

defaultdict_float = defaultdict(float)
defaultdict2_float = defaultdict(lambda: defaultdict(float))
defaultdict3_float = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
list_elemental_path = List[ExtendedNode]
defaultdict_elemental_path = defaultdict(List[list_elemental_path])

dic_hyperpaths = defaultdict(lambda: defaultdict(lambda: defaultdict(List[list_elemental_path])))
dic_labels = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
dic_successors = defaultdict(lambda: defaultdict(lambda: defaultdict(List[ExtendedEdge])))
dic_frequency = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
dic_Vij = defaultdict(lambda: defaultdict(float))
dic_assigment = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
dic_f = defaultdict(float)

dic_boarding = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
dic_alighting = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))

dic_loaded_section = defaultdict(float)


class UsersCost:

    @staticmethod
    def resources_consumer(hyperpaths: dic_hyperpaths, Vij: dic_Vij, assignment: dic_assigment,
                           successors: dic_successors, extended_graph: ExtendedGraph, vp: float, f: defaultdict_float,
                           z: defaultdict2_float, v: defaultdict3_float) -> (float, float, float, int):
        """
        to get resources consumer for all passenger in transport network access time, waiting time,
        time on board of vehicle, numbers of transfer
        :param hyperpaths: Dic[origin: CityNode][destination: CityNode][StopNode] = List[List[ExtendedNodes]]
        :param Vij: dic[origin: CityNode][destination: CityNode] = vij
        :param assignment: dic[origin: CityNode][destination: CityNode][Stop: StopNode] = %V_OD
        :param successors: dic[origin: CityNode][destination: CityNode][ExtendedNode] = List[ExtendedEdge]
        :param extended_graph: ExtendedGraph object
        :param vp: passenger velocity [km/hr]
        :param f: dict with frequency [veh/hr] for each route_id
        :param z: boarding, dic[route_id][direction][stop: StopNode] = pax [pax/veh]
        :param v: alighting, dic[route_id][direction][stop: StopNode] = pax [pax/veh]
        :return: (access time, waiting time, time on boad, numbers of transfers): (float, float, float, int)
        """
        ta = 0
        tv = 0
        te = 0
        t = 0

        edges = extended_graph.get_extended_graph_edges()

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

                    # reportar ta inicial (lateral y tecnologico)
                    ta += vod_s * (stop.mode.tat / 60 + assignment[origin][destination][
                        stop] / 100 * origin.graph_node.width / (4 * vp * stop.mode.d))

                    while len(paths) != 0:
                        nodei, nodej, pax = paths.pop(0)

                        # evita continuar si llegaste a destino
                        if isinstance(nodei, StopNode) and nodei.city_node == destination:
                            continue

                        dis_pax = pax

                        # reportar te
                        if isinstance(nodei, StopNode):
                            if isinstance(nodej, RouteNode):

                                f_acum = 0

                                for suc in successors[origin][destination][nodei]:
                                    f_acum += f[suc.nodej.route.id]

                                dis_pax = dis_pax * (f[nodej.route.id] / f_acum)

                                te += dis_pax * nodei.mode.theta / (f_acum / nodej.route.mode.d)

                        # reportar tv
                        if isinstance(nodei, RouteNode):
                            if isinstance(nodej, RouteNode):
                                for edge in edges:
                                    if edge.nodei == nodei and edge.nodej == nodej:
                                        tv += dis_pax * edge.t
                                        break

                        # reportar transbordos y tv de bajada
                        if isinstance(nodei, RouteNode):
                            if isinstance(nodej, StopNode):
                                # transbordos
                                if nodej.city_node != destination:
                                    t += dis_pax

                                # para tiempo de viaje adicional por esperar la bajada del vehiculo
                                nodei_id = nodei.prev_route_node.stop_node.city_node.graph_node.id
                                nodej_id = nodei.stop_node.city_node.graph_node.id

                                stop_sequence_i = nodei.route.stops_sequence_i

                                index = 0
                                index_i = 0
                                index_j = 0

                                for node_id in stop_sequence_i:
                                    if str(node_id) == str(nodei_id):
                                        index_i = index
                                    if str(node_id) == str(nodej_id):
                                        index_j = index
                                    index = index + 1

                                tb = nodei.route.mode.t / 3600
                                # verificamos si es del sentido de ida
                                if index_i < index_j:
                                    pax_b = v[nodei.route.id]["I"][nodej]
                                    tv += (pax_b * 0.5 * tb) * dis_pax

                                # sentido de vuelta
                                else:
                                    pax_b = v[nodei.route.id]["R"][nodej]
                                    tv += (pax_b * 0.5 * tb) * dis_pax

                        # reportar ta
                        if isinstance(nodei, StopNode):
                            if isinstance(nodej, CityNode):
                                ta += nodei.mode.tat / 60
                        if isinstance(nodej, StopNode):
                            if isinstance(nodei, CityNode):
                                ta += nodej.mode.tat / 60

                        # agregamos elementos faltantes a las rutas
                        # si nodo i, nodo j y nodo k (new suc ) son de rutas entonces
                        for suc in successors[origin][destination][nodej]:
                            # agrega elementos para continuar rutas elementales
                            paths.append((nodej, suc.nodej, dis_pax))

                            # sumaremos tv producido por la espera de los que se bajan en paraderos cuando el ind sigue
                            # en ruta
                            # cbd                                 #SC                             #p
                            if isinstance(nodei, RouteNode) and isinstance(nodej, RouteNode) and isinstance(suc.nodej,
                                                                                                            RouteNode):
                                bya = nodei.route.mode.bya
                                tb = nodei.route.mode.t / 3600
                                # determinamos dirección
                                nodei_id = nodei.stop_node.city_node.graph_node.id
                                nodej_id = nodej.stop_node.city_node.graph_node.id

                                stop_sequence_i = nodei.route.stops_sequence_i

                                index = 0
                                index_i = 0
                                index_j = 0

                                for node_id in stop_sequence_i:
                                    if str(node_id) == str(nodei_id):
                                        index_i = index
                                    if str(node_id) == str(nodej_id):
                                        index_j = index
                                    index = index + 1

                                # verificamos si es del sentido de ida
                                if index_i < index_j:
                                    # simultaneo
                                    if bya == 1:
                                        pasajeros = max(z[nodei.route.id]["I"][nodej.stop_node],
                                                        v[nodei.route.id]["I"][nodej.stop_node])
                                        tv += pasajeros * tb * dis_pax
                                    # secuencial
                                    if bya == 0:
                                        pasajeros = z[nodei.route.id]["I"][nodej.stop_node] + v[nodei.route.id]["I"][
                                            nodej.stop_node]
                                        tv += pasajeros * tb * dis_pax
                                # sentido de vuelta
                                else:
                                    # simultaneo
                                    if bya == 1:
                                        pasajeros = max(z[nodei.route.id]["R"][nodej.stop_node],
                                                        v[nodei.route.id]["R"][nodej.stop_node])
                                        tv += pasajeros * tb * dis_pax
                                    # secuencial
                                    if bya == 0:
                                        pasajeros = z[nodei.route.id]["R"][nodej.stop_node] + v[nodei.route.id]["R"][
                                            nodej.stop_node]
                                        tv += pasajeros * tb * dis_pax

        return ta, te, tv, t

    def get_users_cost(self, hyperpaths: dic_hyperpaths, Vij: dic_Vij, assignment: dic_assigment,
                       successors: dic_successors, extended_graph: ExtendedGraph, f: defaultdict_float,
                       passenger_obj: Passenger, z: defaultdict3_float, v: defaultdict3_float) -> float:
        """
        to get users cost
        :param hyperpaths: Dic[origin: CityNode][destination: CityNode][StopNode] = List[List[ExtendedNodes]]
        :param Vij: dic[origin: CityNode][destination: CityNode] = vij
        :param assignment: dic[origin: CityNode][destination: CityNode][Stop: StopNode] = %V_OD
        :param successors: dic[origin: CityNode][destination: CityNode][ExtendedNode] = List[ExtendedEdge]
        :param extended_graph: ExtendedGraph object
        :param f: dict with frequency [veh/hr] for each route_id
        :param passenger_obj: Passenger obj
        :param z: boarding, dic[route_id][direction][stop: StopNode] = pax [pax/veh]
        :param v: alighting, dic[route_id][direction][stop: StopNode] = pax [pax/veh]
        :return: float, users cost
        """
        ta, te, tv, t = self.resources_consumer(hyperpaths, Vij, assignment, successors,
                                                extended_graph, passenger_obj.va, f, z, v)
        pa = passenger_obj.pa
        pv = passenger_obj.pv
        pw = passenger_obj.pw
        pt = passenger_obj.pt

        return ta * pa + te * pw + tv * pv + t * pt
