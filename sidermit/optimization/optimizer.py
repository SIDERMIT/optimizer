from collections import defaultdict
from typing import List

import numpy as np
from scipy.optimize import minimize, NonlinearConstraint, Bounds, OptimizeResult

from sidermit.city import Graph, Demand
from sidermit.optimization import Constrains
from sidermit.optimization import InfrastructureCost, UsersCost, OperatorsCost
from sidermit.optimization.preoptimization import Assignment, Hyperpath, ExtendedGraph, ExtendedNode, ExtendedEdge
from sidermit.publictransportsystem import Passenger
from sidermit.publictransportsystem import TransportNetwork, Route

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
        # definimos pasajeros
        self.passenger_obj = passenger_obj
        self.vp = self.passenger_obj.va
        self.spa = self.passenger_obj.spa
        self.spv = self.passenger_obj.spv
        self.sPTP = self.passenger_obj.spt

        # definimos red de transporte
        self.network_obj = network_obj

        # definimos frecuencia
        self.f, self.f_opt, self.lines_position = self.f0(f)

        self.extended_graph_obj = ExtendedGraph(self.graph_obj, self.network_obj.get_routes(), self.sPTP, self.f)
        self.hyperpath_obj = Hyperpath(self.extended_graph_obj, self.passenger_obj)

        self.hyperpaths, self.labels, self.successors, self.frequency, self.Vij = self.hyperpath_obj.get_all_hyperpaths(
            self.demand_obj.get_matrix())

        self.assignment = Assignment.get_assignment(self.hyperpaths, self.labels, self.p, self.vp, self.spa, self.spv)

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
    def get_k(routes: List[Route], z: defaultdict3_float, v: defaultdict3_float) -> defaultdict_float:
        """

        :param routes: List[Route]
        :param z: boarding, dic[route_id][direction][stop: StopNode] = pax [pax/veh]
        :param v: alighting, dic[route_id][direction][stop: StopNode] = pax [pax/veh]
        :return:
        """
        most_loaded_section = Assignment.most_loaded_section(routes, z, v)
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

    def constrains(self, z: defaultdict3_float, v: defaultdict3_float, f: defaultdict_float) -> (
            List[float], List[float]):
        """
        to get k constrains and f constrains
        :param z: boarding, dic[route_id][direction][stop: StopNode] = pax [pax/veh]
        :param v: alighting, dic[route_id][direction][stop: StopNode] = pax [pax/veh]
        :param f: dict with frequency [veh/hr] for each route_id
        :return: (k_ineq_constrains, f_ineq_constrains)
        """

        most_loaded_section = Assignment.most_loaded_section(self.network_obj.get_routes(), z, v)

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

        z, v = Assignment.get_alighting_and_boarding(self.Vij, self.hyperpaths, self.successors, self.assignment, f)
        k = self.get_k(self.network_obj.get_routes(), z, v)

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

        z, v = Assignment.get_alighting_and_boarding(self.Vij, self.hyperpaths, self.successors, self.assignment, f)

        most_loaded_section = Assignment.most_loaded_section(self.network_obj.get_routes(), z, v)
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
        res = minimize(self.VRC, self.f_opt, method='trust-constr', constraints=nonlin_con, tol=0.2, bounds=bounds)
        self.print_information_internal_optimization(res)

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

        line = "Internal optimization\n\tSuccess: {}\n\tStatus: {}\n\tMessage: {}\n\tnew_f: {}\n\tConstrain violation: {}".format(
            success, status, message, new_f, constr_violation)
        print(line)
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
            dif += (prev_f[i] - new_f[i]) ** len(prev_f)
        dif = dif ** (1 / len(prev_f))
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
    def external_optimization(graph_obj: Graph, demand_obj: Demand, passenger_obj: Passenger,
                              network_obj: TransportNetwork,
                              f: defaultdict_float = None, tolerance: float = 0.01):
        """

        :param graph_obj: Graph object
        :param demand_obj: Demand object
        :param passenger_obj: Passenger object
        :param network_obj: TransportNetwork object
        :param f: dict with frequency [veh/hr] for each route_id, dic[route_id] = frequency
        :param tolerance: float, tolerance to external optimization
        :return: List[(fopt, success, status, message, constr_violation)]
        """

        list_res = []

        opt_obj = Optimizer(graph_obj, demand_obj, passenger_obj, network_obj, f)
        # inicialización
        list_res.append((opt_obj.f_opt, "initialization", 1, "initialization", 0))

        # primera iteracion
        res = opt_obj.internal_optimization()
        list_res.append((res.x, res.success, res.status, res.message, res.constr_violation))

        pre_f, _, _, _, _ = list_res[0]
        new_f, _, _, _, _ = list_res[1]

        # mientras criterio de tolerancia externo se cumpla
        while not opt_obj.external_optimization_tolerance(pre_f, new_f, tolerance):
            pre_f = new_f
            dic_new_f = opt_obj.fopt_to_f(new_f)
            opt_obj = Optimizer(graph_obj, demand_obj, passenger_obj, network_obj, dic_new_f)
            res = opt_obj.internal_optimization()
            list_res.append((res.x, res.success, res.status, res.message, res.constr_violation))
            new_f = res.x
        return list_res
