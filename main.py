from sidermit.city import Graph, Demand
from sidermit.optimization.preoptimization import ExtendedGraph, Hyperpath, Assignment
from sidermit.optimization import Optimizer, InfrastructureCost, OperatorsCost, UsersCost
from sidermit.publictransportsystem import TransportNetwork, Passenger, TransportMode

from collections import defaultdict

graph_obj = Graph.build_from_parameters(n=8, l=10, g=0.85, p=2)
demand_obj = Demand.build_from_parameters(graph_obj=graph_obj, y=100000, a=0.78, alpha=0.25, beta=0.22)
passenger_obj = Passenger.get_default_passenger()
[bus_obj, metro_obj] = TransportMode.get_default_modes()

network_obj = TransportNetwork(graph_obj=graph_obj)

# circular_routes_bus = network_obj.get_circular_routes(mode_obj=bus_obj)
diametral_routes_bus4 = network_obj.get_diametral_routes(mode_obj=bus_obj, jump=4)
diametral_routes_bus3 = network_obj.get_diametral_routes(mode_obj=bus_obj, jump=3)
tangencial_routes_bus2 = network_obj.get_tangencial_routes(mode_obj=bus_obj, jump=2)

for route in diametral_routes_bus4:
    network_obj.add_route(route_obj=route)

for route in diametral_routes_bus3:
    network_obj.add_route(route_obj=route)

for route in tangencial_routes_bus2:
    network_obj.add_route(route_obj=route)

f = defaultdict(float)

for route in diametral_routes_bus4:
    f[route.id] = 22.2 * 4
for route in diametral_routes_bus3:
    f[route.id] = 22.6 * 4
for route in tangencial_routes_bus2:
    f[route.id] = 21.5 * 4

extended_graph_obj = ExtendedGraph(graph_obj=graph_obj, routes=network_obj.get_routes(), sPTP=passenger_obj.spt,
                                   frequency_routes=f)
hyperpath_obj = Hyperpath(extended_graph_obj=extended_graph_obj, passenger_obj=passenger_obj)

print("calculando hiperrutas")
hyperpaths, labels, successors, frequency, Vij = hyperpath_obj.get_all_hyperpaths(OD_matrix=demand_obj.get_matrix())

print("calculando asignacion")
OD_assignment = Assignment.get_assignment(hyperpaths=hyperpaths, labels=labels, p=2,
                                          vp=passenger_obj.va, spa=passenger_obj.spa,
                                          spv=passenger_obj.spv)

print("calculando z y v")
z, v = Assignment.get_alighting_and_boarding(Vij=Vij, hyperpaths=hyperpaths, successors=successors,
                                             assignment=OD_assignment, f=f)

print(Assignment.str_boarding_alighting(z, v))

opt_obj = Optimizer(graph_obj, demand_obj, passenger_obj, network_obj)

print("k")
k = opt_obj.get_k(network_obj.get_routes(), z, v)
print(k)

CI_obj = InfrastructureCost()
CU_obj = UsersCost()
CO_obj = OperatorsCost()

print("Infrastructure Cost")
X = CI_obj.get_mode_network_distance(graph_obj, network_obj, f)
CI = CI_obj.get_infrastruture_cost(graph_obj,network_obj, f)
print(X)
print("CI = {:.2f}".format(CI/100000))

print("Cost user")
CU = CU_obj.get_users_cost(hyperpaths, Vij, OD_assignment, successors, extended_graph_obj, f, passenger_obj)
ta, te, tv, t = CU_obj.resources_consumer(hyperpaths, Vij, OD_assignment, successors, extended_graph_obj, 4, f)
print("ta: {:.2f}, te: {:.2f}, tv: {:.2f}, T: {:.2f}, CU: {:.2f}".format(ta / 100000 * 60, te / 100000 * 60,
                                                                         tv / 100000 * 60, t, CU/100000))
