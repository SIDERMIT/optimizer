from __future__ import annotations

from collections import defaultdict
from typing import List, Tuple

import numpy as np
from scipy.optimize import minimize, NonlinearConstraint, Bounds, OptimizeResult

from sidermit.city import Graph, Demand
from sidermit.exceptions import *
from sidermit.optimization import Constrains
from sidermit.optimization import InfrastructureCost, UsersCost, OperatorsCost
from sidermit.optimization.preoptimization import Assignment, Hyperpath, ExtendedGraph, ExtendedNode, ExtendedEdge
from sidermit.publictransportsystem import Passenger
from sidermit.publictransportsystem import TransportNetwork, RouteType

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

defaultdict_str = defaultdict(str)


class Optimizer:
    def __init__(self, graph_obj: Graph, demand_obj: Demand, passenger_obj: Passenger, network_obj: TransportNetwork,
                 f: defaultdict_float = None):

        # definimos ciudad
        self.graph_obj = graph_obj
        _, _, _, self.p, _, _, _, _, _ = self.graph_obj.get_parameters()
        # definimos demanda
        self.demand_obj = demand_obj
        self.total_trips = demand_obj.get_total_trips()
        # definimos pasajeros
        self.passenger_obj = passenger_obj
        self.vp = self.passenger_obj.va
        self.pa = self.passenger_obj.pa
        self.pv = self.passenger_obj.pv
        self.TP = self.passenger_obj.pt

        # definimos red de transporte
        self.network_obj = network_obj

        # definimos frecuencia
        self.f, self.f_opt, self.lines_position = self.f0(f)

        self.extended_graph_obj = ExtendedGraph(self.graph_obj, self.network_obj.get_routes(), self.TP, self.f)
        self.hyperpath_obj = Hyperpath(self.extended_graph_obj, self.passenger_obj)

        # en este punto se debería levantar exception de que la red tiene mas de dos modos defnidos
        # o que existe un par OD con viaje y sin conexion
        self.hyperpaths, self.labels, self.successors, self.frequency, self.Vij = self.hyperpath_obj.get_all_hyperpaths(
            self.demand_obj.get_matrix())

        self.assignment = Assignment.get_assignment(self.hyperpaths, self.labels, self.p, self.vp, self.pa,
                                                    self.pv)

        self.len_constrains = len(self.get_constrains(self.f_opt))
        self.len_var = len(self.f_opt)

    def f0(self, f: defaultdict_float = None) -> (defaultdict_float, List[float], defaultdict_str):
        """
        to get a relation between f as a dictionary and f_opt as a list to the optimizer
        :param f: dic[route_id] = frequency [veh/hr] for all D lines
        :return: dic[route_id] = frequency [veh/hr] for all D lines, List[frequency], dic[position] = route_id
        """
        fini = defaultdict(float)
        fopt = []
        lines_position = defaultdict(None)
        n = 0
        if f is None:
            for route in self.network_obj.get_routes():
                fini[route.id] = route.mode.fini
                fopt.append(route.mode.fini)
                lines_position[n] = route.id
                n += 1
        else:
            for route in self.network_obj.get_routes():
                fini[route.id] = f[route.id]
                fopt.append(route.mode.fini)
                lines_position[n] = route.id
                n += 1

        return fini, fopt, lines_position

    def fopt_to_f(self, fopt: List[float]) -> defaultdict_float:
        """
        to get f as a dictionary
        :param fopt: List[frequency]
        :return: dic[route_id] = frequency [veh/hr] all D lines
        """
        f = defaultdict(float)
        n = 0
        for fr in fopt:
            f[self.lines_position[n]] = fr
            n += 1
        return f

    @staticmethod
    def get_k(loaded_section_route: defaultdict3_float) -> defaultdict_float:
        """
        :param loaded_section_route: dic[route_id][direction][stop: StopNode] = pax [pax/veh]
        :return: k: dic[route_id] = vehicle capacity [pax/veh]
        """
        most_loaded_section = Assignment.most_loaded_section(loaded_section_route)
        k = defaultdict(float)
        for route_id in most_loaded_section:
            k[route_id] = most_loaded_section[route_id]
        return k

    def operators_cost(self, z: defaultdict3_float, v: defaultdict3_float, f: defaultdict_float,
                       k: defaultdict_float) -> float:
        """
        to get operators cost
        :param z: boarding, dic[route_id][direction][stop: StopNode] = pax [pax/veh]
        :param v: alighting, dic[route_id][direction][stop: StopNode] = pax [pax/veh]
        :param f: dic[route_id] = frequency [veh/hr]
        :param k: dic[route_id] = frequency [pax/veh]
        :return: float, operator cost
        """
        operators_cost_obj = OperatorsCost()

        edge_distance = self.graph_obj.get_edges_distance()
        routes = self.network_obj.get_routes()
        line_travel_time = operators_cost_obj.lines_travel_time(routes, edge_distance)

        cycle_time = operators_cost_obj.get_cycle_time(z, v, routes, line_travel_time)
        cost = operators_cost_obj.get_operators_cost(routes, cycle_time, f, k)
        return cost

    def infrastructure_cost(self, f: defaultdict_float) -> float:
        """
        to get infrastructure cost
        :param f: dic[route_id] = frequency [veh/hr]
        :return: float, infrastructure cost
        """
        infrastructure_cost_obj = InfrastructureCost()
        cost = infrastructure_cost_obj.get_infrastruture_cost(self.graph_obj, self.network_obj, f)
        return cost

    def user_cost(self, hyperpaths: dic_hyperpaths, Vij: dic_Vij, assignment: dic_assigment,
                  successors: dic_successors, extended_graph: ExtendedGraph, f: defaultdict_float,
                  z: defaultdict3_float, v: defaultdict3_float) -> float:
        """
        to get users cost
        :param hyperpaths: Dic[origin: CityNode][destination: CityNode][StopNode] = List[List[ExtendedNodes]]
        :param Vij: dic[origin: CityNode][destination: CityNode] = vij
        :param assignment: dic[origin: CityNode][destination: CityNode][Stop: StopNode] = %V_OD
        :param successors: dic[origin: CityNode][destination: CityNode][ExtendedNode] = List[ExtendedEdge]
        :param extended_graph: ExtendedGraph object
        :param f: dict with frequency [veh/hr] for each route_id
        :param z: boarding, dic[route_id][direction][stop: StopNode] = pax [pax/veh]
        :param v: alighting, dic[route_id][direction][stop: StopNode] = pax [pax/veh]
        :return: float, users cost
        """
        user_cost_obj = UsersCost()
        cost = user_cost_obj.get_users_cost(hyperpaths, Vij, assignment, successors, extended_graph, f,
                                            self.passenger_obj, z, v)
        return cost

    def constrains(self, loaded_section_route: defaultdict3_float, f: defaultdict_float) -> (
            List[float], List[float]):
        """
        to get k constrains and f constrains
        :param loaded_section_route: dic[route_id][direction][stop: StopNode] = pax [pax/veh]
        :param f: dict with frequency [veh/hr] for each route_id
        :return: (k_ineq_constrains, f_ineq_constrains)
        """

        most_loaded_section = Assignment.most_loaded_section(loaded_section_route)

        constrains_obj = Constrains()

        ineq_k = constrains_obj.most_loaded_section_constrains(self.network_obj.get_routes(), most_loaded_section)
        ineq_f = constrains_obj.fmax_constrains(self.graph_obj, self.network_obj.get_routes(),
                                                self.network_obj.get_modes(), f)

        return ineq_k, ineq_f

    def VRC(self, fopt: List[float]) -> float:
        """
        to get VRC objective function to minime in optimizer
        :param fopt: variable to optimize
        :return: float, VRC value function
        """

        f = self.fopt_to_f(fopt)

        z, v, loaded_section_route = Assignment.get_alighting_and_boarding(self.Vij, self.hyperpaths, self.successors,
                                                                           self.assignment, f)
        k = self.get_k(loaded_section_route)

        CO = self.operators_cost(z, v, f, k)
        CI = self.infrastructure_cost(f)
        CU = self.user_cost(self.hyperpaths, self.Vij, self.assignment, self.successors, self.extended_graph_obj, f, z,
                            v)

        # print("f: {}".format(fopt))
        # print("VRC: {}".format(CO + CI + CU))
        return CO + CI + CU

    def get_constrains(self, fopt: List[float]) -> List[float]:
        """
        to get all constrains as a List[float]
        :param fopt: variable to optimize
        :return: all constrains as a List[float]
        """

        f = self.fopt_to_f(fopt)

        z, v, loaded_section_route = Assignment.get_alighting_and_boarding(self.Vij, self.hyperpaths, self.successors,
                                                                           self.assignment, f)

        most_loaded_section = Assignment.most_loaded_section(loaded_section_route)
        constrain_obj = Constrains()
        ineq_k = constrain_obj.most_loaded_section_constrains(self.network_obj.get_routes(), most_loaded_section)
        ineq_f = constrain_obj.fmax_constrains(self.graph_obj, self.network_obj.get_routes(),
                                               self.network_obj.get_modes(), f)

        con = []
        for c in ineq_k:
            con.append(c)
        for c in ineq_f:
            con.append(c)

        return con

    def internal_optimization(self) -> OptimizeResult:
        """
        method to do internal optimization process, with a hyperpath setted you can get a optimization of the network
        :return:     res : OptimizeResult
        The optimization result represented as a ``OptimizeResult`` object.
        Important attributes are: ``x`` the solution array, ``success`` a
        Boolean flag indicating if the optimizer exited successfully and
        ``message`` which describes the cause of the termination. See
        `OptimizeResult` for a description of other attributes.
        """

        constr_func = lambda fopt: np.array(self.get_constrains(fopt))

        lb = [-1 * np.inf] * self.len_constrains
        ub = [0] * self.len_constrains
        nonlin_con = NonlinearConstraint(constr_func, lb=lb, ub=ub)

        lb = [0] * self.len_var
        ub = [np.inf] * self.len_var

        bounds = Bounds(lb=lb, ub=ub)
        res = minimize(self.VRC, self.f_opt, method='trust-constr', constraints=nonlin_con, tol=0.01, bounds=bounds)
        print(self.print_information_internal_optimization(res))

        return res

    @staticmethod
    def print_information_internal_optimization(res: OptimizeResult) -> str:
        """
        to get a string with information about internal optimization
        :param res: OptimizeResult
        :return: str
        """

        success = res.success
        status = res.status
        message = res.message
        new_f = res.x
        constr_violation = res.constr_violation
        fun = res.fun

        line = "Internal optimization\n\tSuccess: {}\n\tStatus: {}\n\tMessage: {}\n\tnew_f: {}\n\tConstrain violation: {}\n\tVRC: {}".format(
            success, status, message, new_f, constr_violation, fun)
        return line

    @staticmethod
    def f_distance(prev_f: List[float], new_f: List[float]) -> float:
        """
        to get distance between 2 list of frequency results.
        :param prev_f: previous frequency
        :param new_f: new frequency
        :return: float, distance with normal distance
        """
        dif = 0
        for i in range(len(prev_f)):
            dif += abs(prev_f[i] - new_f[i])
        dif = dif  # ** (1 / len(prev_f))
        print("f_norm_distance: {}".format(dif))
        return dif

    def external_optimization_tolerance(self, prev_f: List[float], new_f: List[float], tol: float = 0.01) -> bool:
        """
        True, if tolerance criteria is success
        :param prev_f: previous frequency
        :param new_f: new frequency
        :param tol: float, tolerance
        :return: True, if tolerance criteria is success
        """

        if tol > abs(self.f_distance(prev_f, new_f)):
            return True

        return False

    @staticmethod
    def status_optimization(better_res) -> bool:
        """
        to get a information about status of external optimization
        :param better_res:(fopt, success, status, message, constr_violation, vrc)
        :return: true if status is success, exceptions if not
        """

        if better_res is None:
            raise NoOptimalSolutionFoundException(
                "No optimal solution was found. You can try with other fini or total demand is very large for the proposed network.")

        fopt, success, status, message, constr_violation, fun = better_res

        for f in fopt:
            if f < -0.1:
                raise NegativeFrequencyException("Solution with negative frequency. You can try with other fini")

        if abs(constr_violation) > 0.1:
            raise ConstraintViolationException(
                "Maximum constraint violation at the solution {}. You can try with other fini or total demand is very large for the proposed network.".format(
                    constr_violation))

        if status == 0 or status == 3:
            raise NoOptimalSolutionFoundException(
                "No optimal solution was found. You can try with other fini or total demand is very large for the proposed network.")

        return True

    @staticmethod
    def external_optimization(graph_obj: Graph, demand_obj: Demand, passenger_obj: Passenger,
                              network_obj: TransportNetwork,
                              f: defaultdict_float = None, tolerance: float = 0.01,
                              number_of_iteration: int = None) -> Tuple:
        """
        method to do external optimization process, several iterations of internal optimization with fixed
        hyperpaths in each
        :param graph_obj: Graph object
        :param demand_obj: Demand object
        :param passenger_obj: Passenger object
        :param network_obj: TransportNetwork object
        :param f: dict with frequency [veh/hr] for each route_id, dic[route_id] = frequency
        :param tolerance: float, tolerance to external optimization
        :param number_of_iteration: int, max. number of iterations. Default value is infinity.
        it is recommended to set this value in a small number of iterations (e.x. 5) in the beginning to know if it
        converges
        :return: (fopt, success, status, message, constr_violation, vrc)
        """

        list_res = []

        opt_obj = Optimizer(graph_obj, demand_obj, passenger_obj, network_obj, f)
        # inicialización
        list_res.append((opt_obj.f_opt, "initialization", -1, "initialization", -1, -1))

        # primera iteracion
        res = opt_obj.internal_optimization()
        list_res.append((res.x, res.success, res.status, res.message, res.constr_violation, res.fun))

        pre_f, _, _, _, _, _ = list_res[0]
        new_f, _, _, _, _, _ = list_res[1]

        iteration = 1
        # mientras criterio de tolerancia externo no se cumpla o se llegue al maximo numero de iteraciones
        while not opt_obj.external_optimization_tolerance(pre_f, new_f, tolerance):
            if number_of_iteration is not None:
                if iteration > number_of_iteration:
                    break
            pre_f = new_f
            dic_new_f = opt_obj.fopt_to_f(new_f)
            opt_obj = Optimizer(graph_obj, demand_obj, passenger_obj, network_obj, dic_new_f)
            res = opt_obj.internal_optimization()
            list_res.append((res.x, res.success, res.status, res.message, res.constr_violation, res.fun))
            new_f = res.x
            iteration += 1

        better_result = opt_obj.get_better_result(list_res)

        if opt_obj.status_optimization(better_result):
            return better_result

    @staticmethod
    def get_better_result(list_res):
        valid_result = []
        for x, success, status, message, constr_violation, fun in list_res:
            if status not in [0, 3, -1] and abs(constr_violation) < 0.001:
                cond_f = True
                for f in x:
                    if f < 0:
                        cond_f = False
                        break
                if cond_f:
                    valid_result.append((x, success, status, message, constr_violation, fun))

        better_result = None
        max_fun = float("inf")
        for x, success, status, message, constr_violation, fun in valid_result:
            if fun < max_fun:
                max_fun = fun
                better_result = (x, success, status, message, constr_violation, fun)

        return better_result

    @staticmethod
    def network_optimization(graph_obj: Graph, demand_obj: Demand, passenger_obj: Passenger,
                             network_obj: TransportNetwork,
                             f: defaultdict_float = None, tolerance: float = 0.01,
                             max_number_of_iteration: int = None) -> Tuple:
        """
        obtain optimal frequency for the defined network if possible or raise exceptions in case of not being able
        :param graph_obj: Graph object
        :param demand_obj: Demand object
        :param passenger_obj: Passenger object
        :param network_obj: TransportNetwork object
        :param f: dict with frequency [veh/hr] for each route_id, dic[route_id] = frequency
        :param tolerance: float, tolerance to external optimization
        :param max_number_of_iteration: int, max. number of iterations. Default value is infinity.
        it is recommended to set this value in a small number of iterations (e.x. 5) in the beginning to know if it
        converges
        :return: fopt, success, status, message, constr_violation, vrc
        """

        opt_obj = Optimizer(graph_obj, demand_obj, passenger_obj, network_obj, f)
        better_result = opt_obj.external_optimization(graph_obj, demand_obj, passenger_obj, network_obj, f, tolerance,
                                                      number_of_iteration=max_number_of_iteration)

        print(opt_obj.string_network_optimization(better_result))

        return better_result

    def string_network_optimization(self, res: Tuple) -> str:
        """
        get a str summary about last external optimization in network_optimization
        :param res: Tuple, (fopt, success, status, message, constr_violation, vrc)
        :return:
        """
        fopt, success, status, message, constr_violation, vrc = res
        f = self.fopt_to_f(fopt)

        line = "\n\nOptimization Results"
        line += "\nSuccess: {}".format(success)
        line += "\nStatus: {}".format(status)
        line += "\nMessage: {}".format(message)
        line += "\nMax constrain violation: {}".format(constr_violation)
        line += "\nVRC: {}".format(vrc)
        line += "\n\nFrequency information [veh/hr]: "
        for route_id in f:
            line += "\n\t{}: {:.2f}".format(route_id, f[route_id])

        return line

    def last_iteration(self, res: Tuple):
        """
        return last network optimized with optimization result
        :param res: res: Tuple, (fopt, success, status, message, constr_violation, vrc)
        :return: Optimizer object, boarding dictionary, alighting dictionary, k dictionary, loaded_section_route
        """
        fopt, success, status, message, constr_violation, vrc = res
        f = self.fopt_to_f(fopt)
        final_optimizer = Optimizer(self.graph_obj, self.demand_obj, self.passenger_obj, self.network_obj, f)
        z, v, loaded_section_route = Assignment.get_alighting_and_boarding(final_optimizer.Vij,
                                                                           final_optimizer.hyperpaths,
                                                                           final_optimizer.successors,
                                                                           final_optimizer.assignment, f)
        k = self.get_k(loaded_section_route)
        return final_optimizer, z, v, k, loaded_section_route

    def network_results(self, res: Tuple) -> List[Tuple]:
        """
        to get transport network results per line-direction
        :param res: optimization result: Tuple, (fopt, success, status, message, constr_violation, vrc)
        :return: List[(route.id: str, f [veh/hr]: float, k [pax/veh]: float, B [veh]: float, cycle_time [hr]: float,
        CO [US$/hr-pax]: float, lambda_min, sub_table_i: List[(node_i, node_j, lambda)],
        sub_table_i: List[(node_i, node_j, lambda)]
        """
        output = []

        fopt, success, status, message, constr_violation, vrc = res
        final_optimizer, z, v, k, loaded_section_route = self.last_iteration(res)

        f = self.fopt_to_f(fopt)

        # resultados de modos
        travel_time_line = OperatorsCost.lines_travel_time(final_optimizer.network_obj.get_routes(),
                                                           final_optimizer.graph_obj.get_edges_distance())
        cycle_time_line = OperatorsCost.get_cycle_time(z, v, final_optimizer.network_obj.get_routes(), travel_time_line)

        for route in final_optimizer.network_obj.get_routes():

            # flota de buses
            b = cycle_time_line[route.id] * f[route.id]
            nodes_sequence_i = route.nodes_sequence_i
            nodes_sequence_r = route.nodes_sequence_r
            # carga que hay en los tramos
            total_pax = 0
            charge_i = []
            charge_r = []
            # total de subidas a la ruta
            total_b = 0

            # caso circular
            if route._type == RouteType.CIRCULAR:

                # circular con sentido de ida
                if len(nodes_sequence_i) > 0:
                    node_sequence = nodes_sequence_i
                    direction = "I"
                # circular con sentido de vuelta
                else:
                    node_sequence = nodes_sequence_r
                    direction = "R"
                load_i = []
                for i in node_sequence:
                    for stop_node in z[route.id][direction]:
                        if stop_node.city_node.graph_node.id == i:
                            total_b += z[route.id][direction][stop_node]
                            break
                    for stop_node in loaded_section_route[route.id][direction]:
                        if stop_node.city_node.graph_node.id == i:
                            load_i.append(loaded_section_route[route.id][direction][stop_node])
                            break

                if total_b == 0:
                    co = 0
                else:
                    co = (route.mode.co + route.mode.c1 * k[route.id]) * f[route.id] * cycle_time_line[route.id] / (
                            total_b * f[route.id])

                if len(load_i) >= 1:
                    charge_min = min(load_i) / max(load_i)
                else:
                    load_i = [1] * len(node_sequence)
                    charge_min = 0

                sub_table = []
                sub_table_i = []
                sub_table_r = []

                node_i = None
                charge_ij = None
                for i in range(len(node_sequence)):
                    if i == 0:
                        node_i = node_sequence[i]
                        charge_ij = load_i[i] / max(load_i)
                        continue
                    else:
                        node_j = node_sequence[i]
                        sub_table.append((node_i, node_j, abs(charge_ij)))
                        node_i = node_j
                        charge_ij = load_i[i] / max(load_i)

                # circular con sentido de ida
                if len(nodes_sequence_i) > 0:
                    sub_table_i = sub_table
                # circular con sentido de vuelta
                else:
                    sub_table_r = sub_table

                output.append((
                    route.id, f[route.id], f[route.id] / route.mode.d, k[route.id], b, cycle_time_line[route.id] * 60,
                    co, abs(charge_min), sub_table_i, sub_table_r))
            else:
                # z and v: dic[route_id][direction][stop: StopNode] = pax [pax/veh]
                total_pax = 0
                for node_id in nodes_sequence_i:
                    bool_add = False
                    for stopnode in z[route.id]["I"]:
                        if stopnode.city_node.graph_node.id == node_id:
                            pax_b = z[route.id]["I"][stopnode]
                            pax_a = v[route.id]["I"][stopnode]
                            total_pax += pax_b - pax_a
                            total_b += pax_b
                            # print(str(node_id), total_pax, k[route.id], route.id, "I")
                            charge_i.append((node_id, total_pax / k[route.id]))
                            bool_add = True
                            break
                    if bool_add is False:
                        # print(str(node_id), total_pax, k[route.id], route.id, "I", "no add")
                        charge_i.append((node_id, total_pax / k[route.id]))

                total_pax = 0
                for node_id in nodes_sequence_r:
                    bool_add = False
                    for stopnode in z[route.id]["R"]:
                        if stopnode.city_node.graph_node.id == node_id:
                            pax_b = z[route.id]["R"][stopnode]
                            pax_a = v[route.id]["R"][stopnode]
                            total_pax += pax_b - pax_a
                            total_b += pax_b
                            # print(str(node_id), total_pax, k[route.id], route.id, "R")
                            charge_r.append((node_id, total_pax / k[route.id]))
                            bool_add = True
                            break
                    if bool_add is False:
                        # print(str(node_id), total_pax, k[route.id], route.id, "R", "no add")
                        charge_r.append((node_id, total_pax / k[route.id]))

                co = (route.mode.co + route.mode.c1 * k[route.id]) * f[route.id] * cycle_time_line[route.id] / (
                        total_b * f[route.id])

                charge_min = float("inf")
                sub_table_i = []
                node_i = None
                charge_ij = None
                for node_j, charge in charge_i:
                    if node_i is None:
                        node_i = node_j
                        charge_ij = charge
                        continue
                    else:
                        sub_table_i.append((node_i, node_j, abs(charge_ij)))
                        if charge_min > charge_ij:
                            charge_min = charge_ij
                        node_i = node_j
                        charge_ij = charge

                sub_table_r = []
                node_i = None
                charge_ij = None
                for node_j, charge in charge_r:
                    if node_i is None:
                        node_i = node_j
                        charge_ij = charge
                        continue
                    else:
                        sub_table_r.append((node_i, node_j, abs(charge_ij)))
                        if charge_min > charge_ij:
                            charge_min = charge_ij
                        node_i = node_j
                        charge_ij = charge

                output.append((
                    route.id, f[route.id], f[route.id] / route.mode.d, k[route.id], b, cycle_time_line[route.id] * 60,
                    co, abs(charge_min), sub_table_i, sub_table_r))

        return output

    @staticmethod
    def string_network_results(output_network_results: List[Tuple]) -> str:
        """
        to get a string with network results
        :param output_network_results: List[(route.id: str, f [veh/hr]: float, k [pax/veh]: float, B [veh]: float,
        cycle_time [hr]: float, CO [US$/hr-pax]: float, lambda_min, sub_table_i: List[(node_i, node_j, lambda)],
        sub_table_i: List[(node_i, node_j, lambda)]
        :return: str
        """
        line = "route_id;F[veh/hr];f[veh/hr-line];k[pax/veh];B[veh];tc[min];CO[US$/hr-pax];load_min;sub_table_i;sub_table_r"

        for route_id, F, f, k, b, cycle_time, co, charge_min, sub_table_i, sub_table_r in output_network_results:
            line += "\n{};{:.2f};{:.2f};{:.2f};{:.2f};{:.2f};{:.2f};{:.2f};{};{}".format(route_id, F, f, k, b,
                                                                                        cycle_time, co,
                                                                                        charge_min, sub_table_i,
                                                                                        sub_table_r)
        return line

    def write_file_network_results(self, file_path, output_network_results: List[Tuple]) -> None:
        """
        to write output file with result of optimization transport network
        :param file_path: file path
        :param output_network_results: List[(route.id: str, f [veh/hr]: float, k [pax/veh]: float, B [veh]: float,
        cycle_time [hr]: float, CO [US$/hr-pax]: float, lambda_min, sub_table_i: List[(node_i, node_j, lambda)],
        sub_table_i: List[(node_i, node_j, lambda)]
        :return: None
        """
        string_lines = self.string_network_results(output_network_results)
        file = open(file_path, 'w', encoding='utf-8')
        file.write(string_lines)
        file.close()

    def overall_results(self, res: Tuple) -> defaultdict:
        """
        to get overall cost results per passenger
        :param res: optimization result: Tuple, (fopt, success, status, message, constr_violation, vrc)
        :return: defaultdict:

        Key [unit]: value type

        VRC [USD$/hr-pax]: float,
        operators_cost [USD$/hr-pax]: float,
        infrastructure_cost [USD$/hr-pax]: float,
        users_cost [USD$/hr-pax]: float,
        travel_time_on_board [min/pax]: float,
        waiting time [min/pax]: float,
        access_time [min/pax]: float,
        transfers [transfer/pax]: float,
        vehicles_mode [veh/mode]: dic[TransportMode] = float [veh],
        vehicle_capacity_mode [pax/veh]: dic[TransportMode] = float [pax/veh],
        lines_mode : dic[TransportMode]=int [lines])
        """
        fopt, success, status, message, constr_violation, vrc = res
        final_optimizer, z, v, k, loaded_section_route = self.last_iteration(res)

        f = self.fopt_to_f(fopt)

        # resultados de costos
        CO = self.operators_cost(z, v, f, k)
        CI = self.infrastructure_cost(f)
        CU = self.user_cost(final_optimizer.hyperpaths, final_optimizer.Vij, final_optimizer.assignment,
                            final_optimizer.successors, final_optimizer.extended_graph_obj, f, z, v)

        VRC = CO + CI + CU

        # resultados de usuarios
        ta, te, tv, t = UsersCost.resources_consumer(final_optimizer.hyperpaths, final_optimizer.Vij,
                                                     final_optimizer.assignment, final_optimizer.successors,
                                                     final_optimizer.extended_graph_obj,
                                                     final_optimizer.passenger_obj.va, f, z, v)

        # resultados de modos
        travel_time_line = OperatorsCost.lines_travel_time(final_optimizer.network_obj.get_routes(),
                                                           final_optimizer.graph_obj.get_edges_distance())
        cycle_time_line = OperatorsCost.get_cycle_time(z, v, final_optimizer.network_obj.get_routes(), travel_time_line)

        B = defaultdict(float)
        L = defaultdict(int)

        K_list = defaultdict(list)
        K = defaultdict(float)

        for route in self.network_obj.get_routes():
            if f[route.id] > 0:
                B[route.mode] += f[route.id] * cycle_time_line[route.id]
                L[route.mode] += route.mode.d
                K_list[route.mode].append(k[route.id])

        for mode in K_list:
            l = K_list[mode]
            K[mode] = sum(l) / len(l)

        output = defaultdict(None)
        output["VRC"] = VRC / self.total_trips
        output["operators_cost"] = CO / self.total_trips
        output["infrastructure_cost"] = CI / self.total_trips
        output["users_cost"] = CU / self.total_trips
        output["travel_time_on_board"] = tv / self.total_trips * 60
        output["waiting_time"] = te / self.total_trips * 60
        output["access_time"] = ta / self.total_trips * 60
        output["transfers"] = t / self.total_trips
        output["vehicles_mode"] = B
        output["vehicle_capacity_mode"] = K
        output["lines_mode"] = L
        return output

    @staticmethod
    def string_overall_results(overall_results: defaultdict) -> str:
        """
        to get a string to print overall results in console
        :param overall_results: defaultdict

        Key [unit]: value type

        VRC [USD$/hr-pax]: float,
        operators_cost [USD$/hr-pax]: float,
        infrastructure_cost [USD$/hr-pax]: float,
        users_cost [USD$/hr-pax]: float,
        travel_time_on_board [min/pax]: float,
        waiting time [min/pax]: float,
        access_time [min/pax]: float,
        transfers [transfer/pax]: float,
        vehicles_mode [veh/mode]: dic[TransportMode] = float [veh],
        vehicle_capacity_mode [pax/veh]: dic[TransportMode] = float [pax/veh],
        lines_mode : dic[TransportMode]=int [lines])
        :return: string to print overall results in console
        """
        vrc = overall_results["VRC"]
        co = overall_results["operators_cost"]
        ci = overall_results["infrastructure_cost"]
        cu = overall_results["users_cost"]
        tv = overall_results["travel_time_on_board"]
        te = overall_results["waiting_time"]
        ta = overall_results["access_time"]
        t = overall_results["transfers"]
        b = overall_results["vehicles_mode"]
        k = overall_results["vehicle_capacity_mode"]
        l = overall_results["lines_mode"]

        line = "\n\nObjective function VRC [USD$/hr-pax]: {:.2f}".format(vrc)
        line += "\nOperators cost [USD$/hr-pax]        : {:.2f}".format(co)
        line += "\nInfrastructure cost [USD$/hr-pax]   : {:.2f}".format(ci)
        line += "\nUsers cost [USD$/hr-pax]            : {:.2f}".format(cu)

        line += "\n\nResources consumer for users"
        line += "\nTime on board vehicle [min/pax]: {:.2f}".format(tv)
        line += "\nWaiting time [min/pax]         : {:.2f}".format(te)
        line += "\nAccess time [min/pax]          : {:.2f}".format(ta)
        line += "\ntotal travel time [min/pax]    : {:.2f}".format(tv + ta + te)
        line += "\nTransfers [transfers/pax]      : {:.2f}".format(t)

        line += "\n\n"
        line += "Transport mode information: {}".format(len(b))

        for mode in b:
            line += "\n\n\tMode name: {}".format(mode.name)
            line += "\n\tB [veh]      : {:.2f}".format(b[mode])
            line += "\n\tK [pax/veh]  : {:.2f}".format(k[mode])
            line += "\n\tL [lines]    : {}".format(l[mode])

        return line
