from sidermit.preoptimization import RouteNode, StopNode, ExtendedGraph, CityNode
from sidermit.publictransportsystem import Passenger


class UsersCost:

    @staticmethod
    def resources_consumer(hyperpaths, Vij, assignment, successors, extended_graph: ExtendedGraph, vp, f):
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

                    # reportar ta inicial (lateral y tecnologico
                    ta += vod_s * (stop.mode.tat / 60 + assignment[origin][destination][
                        stop] / 100 * origin.graph_node.width / 4 * vp)

                    while len(paths) != 0:
                        nodei, nodej, pax = paths.pop(0)

                        # evita continuar si llegaste a destino
                        if isinstance(nodei, CityNode) and nodei == destination:
                            continue

                        dis_pax = pax

                        # reportar te
                        if isinstance(nodei, StopNode):
                            if isinstance(nodej, RouteNode):

                                f_acum = 0

                                for suc in successors[origin][destination][nodei]:
                                    f_acum += f[suc.nodej.route.id]

                                dis_pax = pax * (f[nodej.route.id] / f_acum)

                                te += dis_pax * nodei.mode.theta / (f_acum / nodej.route.mode.d)

                        # reportar tv
                        if isinstance(nodei, RouteNode):
                            if isinstance(nodej, RouteNode):
                                for edge in edges:
                                    if edge.nodei == nodei and edge.nodej == nodej:
                                        tv += dis_pax * edge.t
                                        break

                        # reportar transbordos
                        if isinstance(nodei, RouteNode):
                            if isinstance(nodej, StopNode):
                                if nodej.city_node != destination:
                                    t += dis_pax

                        # reportar ta
                        if isinstance(nodei, StopNode):
                            if isinstance(nodej, CityNode):
                                ta += nodei.mode.tat / 60
                        if isinstance(nodej, StopNode):
                            if isinstance(nodei, CityNode):
                                ta += nodej.mode.tat / 60

                        # agregamos elementos faltantes a las rutas
                        for suc in successors[origin][destination][nodej]:
                            paths.append((nodej, suc.nodej, dis_pax))

        return ta, te, tv, t

    def get_users_cost(self, hyperpaths, Vij, assignment, successors, extended_graph: ExtendedGraph, f,
                       passenger_obj: Passenger):
        ta, te, tv, t = self.resources_consumer(hyperpaths, Vij, assignment, successors,
                                                extended_graph, passenger_obj.va, f)
        pa = passenger_obj.pa
        pv = passenger_obj.pv
        pw = passenger_obj.spw
        pt = passenger_obj.pt

        return ta * pa + te * pw + tv * pv + t * pt
