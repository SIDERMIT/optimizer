from sidermit.city import Graph, Demand
from sidermit.optimization.preoptimization import ExtendedGraph, Hyperpath, Assignment
from sidermit.publictransportsystem import TransportNetwork, Passenger, TransportMode

from collections import defaultdict

graph_obj = Graph.build_from_parameters(n=8, l=10, g=0.85, p=2)
demand_obj = Demand.build_from_parameters(graph_obj=graph_obj, y=100000, a=0.78, alpha=0.25, beta=0.22)
passenger_obj = Passenger.get_default_passenger()
[bus_obj, metro_obj] = TransportMode.get_default_modes()

network_obj = TransportNetwork(graph_obj=graph_obj)

circular_routes_bus = network_obj.get_circular_routes(mode_obj=bus_obj)
diametral_routes_bus4 = network_obj.get_diametral_routes(mode_obj=bus_obj, jump=4)
diametral_routes_bus3 = network_obj.get_diametral_routes(mode_obj=bus_obj, jump=3)
radial_routes_bus = network_obj.get_radial_routes(mode_obj=bus_obj, short=True)

for route in circular_routes_bus:
    network_obj.add_route(route_obj=route)

for route in diametral_routes_bus4:
    network_obj.add_route(route_obj=route)

for route in diametral_routes_bus3:
    network_obj.add_route(route_obj=route)

for route in radial_routes_bus:
    network_obj.add_route(route_obj=route)

f = defaultdict(float)

for route in circular_routes_bus:
    f[route.id] = 119.982243597959
for route in diametral_routes_bus4:
    f[route.id] = 48.0203401589406
for route in diametral_routes_bus3:
    f[route.id] = 48.0203401589406
for route in radial_routes_bus:
    f[route.id] = 0.0000000301844242487092

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


