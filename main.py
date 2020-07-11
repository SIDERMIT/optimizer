from sidermit.city import Graph, Demand
from sidermit.publictransportsystem import Route, TransportNetwork, TransportModeManager, Passenger, TransportMode
from sidermit.preoptimization import ExtendedGraph
from sidermit.preoptimization import Hyperpath
from collections import defaultdict

# graph_obj = Graph.build_from_parameters(n=8, l=10000, g=0.85, p=2)
#
# [bus_obj, metro_obj] = TransportMode.get_default_modes()
#
# passenger = Passenger(1, 1, 2, 3, 16, 1, 2, 3, 16)
#
# network = TransportNetwork(graph_obj)
#
#
# diametral4_metro = network.get_diametral_routes(metro_obj, jump=4)
# circulares_metro = network.get_circular_routes(metro_obj)
#
# circulares = network.get_circular_routes(bus_obj)
# diametral4 = network.get_diametral_routes(bus_obj, jump=4)
# diametral3 = network.get_diametral_routes(bus_obj, jump=3)
# tangencial1 = network.get_tangencial_routes(bus_obj, jump=1)
# tangencial2 = network.get_tangencial_routes(bus_obj, jump=2)
# radial = network.get_radial_routes(bus_obj)
# radialc = network.get_radial_routes(bus_obj, short=True)
# feeder = network.get_feeder_routes(bus_obj)
# diametralc4 = network.get_diametral_routes(bus_obj, jump=4, short=True)
# diametralc3 = network.get_diametral_routes(bus_obj, jump=3, short=True)
# tangencialc1 = network.get_tangencial_routes(bus_obj, jump=1, short=True)
# tangencialc2 = network.get_tangencial_routes(bus_obj, jump=2, short=True)
#
#
# for route in diametral4_metro:
#     network.add_route(route)
# for route in circulares_metro:
#     network.add_route(route)
# for route in feeder:
#     network.add_route(route)
# for route in radialc:
#     network.add_route(route)
#
# for route in circulares:
#     network.add_route(route)
# for route in diametral4:
#     network.add_route(route)
# for route in diametral3:
#     network.add_route(route)
# for route in tangencial1:
#     network.add_route(route)
# for route in tangencial2:
#     network.add_route(route)
# for route in radial:
#     network.add_route(route)
# for route in diametralc4:
#     network.add_route(route)
# for route in diametralc3:
#     network.add_route(route)
# for route in tangencialc1:
#     network.add_route(route)
# for route in tangencialc2:
#     network.add_route(route)
#
# # network.plot("sidermit.png")
#
# frequency = defaultdict(float)
#
# routes = network.get_routes()
# routes_id = []
#
# for route in routes:
#     routes_id.append(route.id)
#
# for route_id in routes_id:
#     frequency[route_id] = 24
#
# extended_graph = ExtendedGraph(graph_obj, network.get_routes(), passenger.spt, frequency)
# # print(extended_graph.__str__())
#
# # para obtener un par OD para algoritmos que vienen
# extended_graph_nodes = extended_graph.get_extended_graph_nodes()
# SC1 = None
# SC4 = None
# P1 = None
# CBD = None
# SC7 = None
# for city_node in extended_graph_nodes:
#     if str(city_node.graph_node.name) == "P_1":
#         P1 = city_node
#     if str(city_node.graph_node.name) == "CBD":
#         CBD = city_node
#     if str(city_node.graph_node.name) == "SC_1":
#         SC1 = city_node
#     if str(city_node.graph_node.name) == "SC_4":
#         SC4 = city_node
#     if str(city_node.graph_node.name) == "SC_7":
#         SC7 = city_node
#
# # generamos hiperruta para un par de nodos de origen y destino
# hyperpath_obj = Hyperpath(extended_graph, passenger)
# successors, label, frequencies = hyperpath_obj.build_hyperpath_graph(P1, SC1)
# # print(hyperpath_obj.string_hyperpath_graph(successors, label, frequencies))
#
# # obtenemos hiperrutas
#
# hyperpath_OD, label, successors = hyperpath_obj.get_hyperpath_OD(P1, SC1)
# string_HP_OD = hyperpath_obj.string_hyperpaths_OD(hyperpath_OD, label)
# print(string_HP_OD)
#
# hyperpath_obj.plot(hyperpath_OD)

# demand_obj = Demand.build_from_parameters(graph_obj=graph_obj, y=1000, a=0.5, alpha=1 / 3, beta=1 / 3)
# OD_matrix = demand_obj.get_matrix()
#
# hyperpaths, labels, successors = hyperpath_obj.get_all_hyperpaths(OD_matrix)
# print(hyperpath_obj.string_all_hyperpaths(hyperpaths, labels, successors))

#
# graph_obj = Graph.build_from_parameters(n=2, l=10000, g=0.5, p=2)
#
# demand_obj = Demand.build_from_parameters(graph_obj=graph_obj, y=1000, a=0.5, alpha=1 / 3, beta=1 / 3)
# OD_matrix = demand_obj.get_matrix()
#
# mode_manager = TransportModeManager()
# bus_obj = mode_manager.get_mode("bus")
# metro_obj = mode_manager.get_mode("metro")
#
# passenger_obj = Passenger.get_default_passenger()
#
# network = TransportNetwork(graph_obj)
#
# # agregamos rutas a la red
# feeder_routes = network.get_feeder_routes(bus_obj)
# radial_routes = network.get_radial_routes(metro_obj, short=True)
# radial_routes_bus = network.get_radial_routes(bus_obj)
# circular_routes = network.get_circular_routes(bus_obj)
#
# for route in feeder_routes:
#     network.add_route(route)
#
# for route in radial_routes:
#     network.add_route(route)
#
# for route in circular_routes:
#     network.add_route(route)
#
# for route in radial_routes_bus:
#     network.add_route(route)
#
# # generamos grafo extendido
# extended_graph = ExtendedGraph(graph_obj, network.get_routes(), passenger_obj.spt)
# print(extended_graph.__str__())
#
# # para obtener un par OD para algoritmos que vienen
# extended_graph_nodes = extended_graph.get_extended_graph_nodes()
# P1 = None
# CBD = None
# for city_node in extended_graph_nodes:
#     if str(city_node.graph_node.name) == "CBD":
#         CBD = city_node
#     if str(city_node.graph_node.name) == "P_1":
#         P1 = city_node
#
# # generamos hiperruta para un par de nodos de origen y destino
# hyperpath_obj = Hyperpath(extended_graph, passenger_obj)
# successors, label, frequencies = hyperpath_obj.build_hyperpath_graph(P1, CBD)
# print(hyperpath_obj.string_hyperpath_graph(successors, label, frequencies))
#
# # obtenemos hiperrutas
# hyperpath_OD, label, successor = hyperpath_obj.get_hyperpath_OD(P1, CBD)
# string_HP_OD = hyperpath_obj.string_hyperpaths_OD(hyperpath_OD, label)
# print(string_HP_OD)
#
# print("Penalidad de transbordo: {} [min]".format(passenger_obj.spt))
#
# # hyperpath_obj.plot(hyperpath_OD)
#
# hyperpaths, labels, successors = hyperpath_obj.get_all_hyperpaths(OD_matrix)
# print(hyperpath_obj.string_all_hyperpaths(hyperpaths, labels, successors))
#


graph_obj = Graph.build_from_parameters(n=2, l=10000, g=0.5, p=2000)

demand_obj = Demand.build_from_parameters(graph_obj, y=1000, a=0.5, alpha=1 / 3, beta=1 / 3)
OD_matrix = demand_obj.get_matrix()

[bus_obj, metro_obj] = TransportMode.get_default_modes()

passenger_obj = Passenger.get_default_passenger()

network_obj = TransportNetwork(graph_obj)
radial = network_obj.get_radial_routes(bus_obj)
diametral = network_obj.get_diametral_routes(bus_obj, jump=1)
diametral_metro = network_obj.get_diametral_routes(metro_obj, jump=1)

for route in radial:
    network_obj.add_route(route)
for route in diametral:
    network_obj.add_route(route)
for route in diametral_metro:
    network_obj.add_route(route)

extended_graph_obj = ExtendedGraph(graph_obj, network_obj.get_routes(), 16)

nodes = extended_graph_obj.get_extended_graph_nodes()

P1 = None
SC2 = None
stop_bus = None
stop_metro = None
for city_node in nodes:
    if city_node.graph_node.name == str("P_1"):
        P1 = city_node
        for stop in nodes[city_node]:
            if stop.mode.name == "bus":
                stop_bus = stop
            if stop.mode.name == "metro":
                stop_metro = stop
    if city_node.graph_node.name == str("SC_2"):
        SC2 = city_node

print(P1)
print(SC2)
print(stop_bus)
print(stop_metro)

hyper_path_obj = Hyperpath(extended_graph_obj, passenger_obj)

hyperpaths, labels, successors = hyper_path_obj.get_all_hyperpaths(OD_matrix)

print(labels[P1][SC2][stop_bus])
print(labels[P1][SC2][stop_metro])





#
# for origin in hyperpaths:
#     print("new_origin")
#     print(id(origin))
#     print(origin.graph_node.name)
#     for destination in hyperpaths[origin]:
#         print("new_destination")
#         print(id(destination))
#         print(destination.graph_node.name)
#         for node in hyperpaths[origin][destination]:
#             print("new_node")
#             print(id(node))
#             print(node.mode.name)

# from sidermit.preoptimization import StopNode
# print()
# print("labels")
# for origin in labels:
#     print("new_origin")
#     print(id(origin))
#     print(origin.graph_node.name)
#     for destination in labels[origin]:
#         print("new_destination")
#         print(id(destination))
#         print(destination.graph_node.name)
#         for node in labels[origin][destination]:
#             if isinstance(node, StopNode):
#                 if node.city_node == origin:
#                     print("new_node")
#                     print(id(node))
#                     print(node.mode.name)


# self.assertEqual(round(labels[P1][P2][stop_bus], 5), 1.37738)
# self.assertEqual(round(labels[P1][P2][stop_metro], 5), 0.83571)
#
# self.assertEqual(len(hyperpaths), 4)
# self.assertEqual(len(hyperpaths[P1]), 3)
# self.assertEqual(len(hyperpaths[P2]), 3)