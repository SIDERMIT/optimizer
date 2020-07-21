from .infrastructure_cost import InfrastructureCost
from .users_cost import UsersCost
from .operators_cost import OperatorsCost
from .constrains import Constrains
from sidermit.publictransportsystem import Passenger
from sidermit.preoptimization import ExtendedGraph

from scipy.optimize import minimize, NonlinearConstraint
from sidermit.city import Graph
from sidermit.publictransportsystem import TransportNetwork


class Optimizer:

    @staticmethod
    def operators_cost(graph_obj: Graph, network_obj: TransportNetwork, z, v, f, k):
        operators_cost_obj = OperatorsCost()

        edge_distance = graph_obj.get_edges_distance()
        routes = network_obj.get_routes()
        line_travel_time = operators_cost_obj.lines_travel_time(routes, edge_distance)

        cycle_time = operators_cost_obj.get_cycle_time(z, v, routes, line_travel_time)
        cost = operators_cost_obj.get_operators_cost(routes, cycle_time, f, k)
        return cost


    @staticmethod
    def infrastructure_cost(graph_obj: Graph, network_obj: TransportNetwork, f):

        infrastructure_cost_obj = InfrastructureCost()
        cost = infrastructure_cost_obj.get_infrastruture_cost(graph_obj, network_obj, f)
        return cost

    @staticmethod
    def user_cost(hyperpaths, Vij, assignment, successors, extended_graph: ExtendedGraph, f, passenger_obj: Passenger):
        user_cost_obj = UsersCost()
        cost = user_cost_obj.get_users_cost(hyperpaths, Vij, assignment, successors, extended_graph, f, passenger_obj)
        return cost

    @staticmethod
    def constrains(graph_obj: Graph, network_obj: TransportNetwork, z, v, f, k):
        constrains_obj = Constrains()

        eq_k, ineq_k = constrains_obj.most_loaded_section_constrains(network_obj.get_routes(), z, v, k)
        ineq_f = constrains_obj.fmax_constrains(graph_obj, network_obj.get_routes(), network_obj.get_modes(), f)

        return eq_k, ineq_k, ineq_f




