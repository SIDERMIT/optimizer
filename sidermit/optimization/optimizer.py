from .infrastructure_cost import InfrastructureCost
from .users_cost import UsersCost
from .operators_cost import OperatorsCost
from .constrains import Constrains
from sidermit.publictransportsystem import Passenger
from sidermit.preoptimization import ExtendedGraph

from scipy.optimize import minimize, NonlinearConstraint
from sidermit.city import Graph, Demand
from sidermit.publictransportsystem import TransportNetwork

from collections import defaultdict


class Optimizer:
    def __init__(self, graph_obj: Graph, passenger_obj: Passenger, network_obj: TransportNetwork):
        self.graph_obj = graph_obj
        self.passenger_obj = passenger_obj
        self.network_obj = network_obj

        self.f, self.f_opt, self.lines_position = self.finit(network_obj)



    def operators_cost(self, z, v, f, k):
        operators_cost_obj = OperatorsCost()

        edge_distance = self.graph_obj.get_edges_distance()
        routes = self.network_obj.get_routes()
        line_travel_time = operators_cost_obj.lines_travel_time(routes, edge_distance)

        cycle_time = operators_cost_obj.get_cycle_time(z, v, routes, line_travel_time)
        cost = operators_cost_obj.get_operators_cost(routes, cycle_time, f, k)
        return cost

    def infrastructure_cost(self, f):
        infrastructure_cost_obj = InfrastructureCost()
        cost = infrastructure_cost_obj.get_infrastruture_cost(self.graph_obj, self.network_obj, f)
        return cost

    def user_cost(self, hyperpaths, Vij, assignment, successors, extended_graph: ExtendedGraph, f):
        user_cost_obj = UsersCost()
        cost = user_cost_obj.get_users_cost(hyperpaths, Vij, assignment, successors, extended_graph, f,
                                            self.passenger_obj)
        return cost

    def constrains(self, z, v, f, k):
        constrains_obj = Constrains()

        eq_k, ineq_k = constrains_obj.most_loaded_section_constrains(self.network_obj.get_routes(), z, v, k)
        ineq_f = constrains_obj.fmax_constrains(self.graph_obj, self.network_obj.get_routes(),
                                                self.network_obj.get_modes(), f)

        return eq_k, ineq_k, ineq_f

    @staticmethod
    def finit(network_obj: TransportNetwork):
        f = defaultdict(float)
        fopt = []
        lines_position = defaultdict(int)
        n = 0
        for route in network_obj.get_routes():
            f[route.id] = 28
            fopt.append(28)
            lines_position[route.id] = n
            n += 1

        return f, fopt, lines_position

    def fopt_to_f(self, fopt):
        pass

    def kinit(self, f):
        pass

    def fopt_in_f(self, fopt):
        pass

    def VRC(self, fopt):
        pass
