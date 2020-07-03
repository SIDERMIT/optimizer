# from matrixod import matrixod
# from city_graph import city_graph
# from draw import plot_city
# from transit_network import transit_network
#
# dir_out = r"C:\Users\felip\Downloads\esteb\output"
# # path = r"C:\Users\felip\Downloads\esteb\inputs\matriz.txt"
#
# ############## PARAMETROS DE CIUDAD #############
# n = 8
# L = 10000
# g = 0.5
# p = 2
# etha = 1
# etha_zone = 3
# angles = [10, 60, 150, 160, 180, 240, 250, 355]
# Gi = [0.5, 1, 0.5, 1, 0.5, 1, 0.5, 1]
# Hi = [1, 2, 1, 2, 1, 2, 1, 2]
# ############## MODULO DE CIUDAD #############
# # falta definir integracion de informacion de nodes y arcos
# # validacion de archivos externos
# # validacion geométrica de parámetros
# c = city_graph(n, L=L, g=g, etha=etha, etha_zone=etha_zone, angles=angles, Gi=Gi, Hi=Hi)
# print(c.text_parameters)
# if c.plot:
#     print("Informacion de nodos")
#     print(c.nodes)
#     print("Informacion de nodos")
#     print(c.edges)
# # ############## PARAMETROS DE DEMANDA #############
# y = 1000
# a = 0.5
# alpha = 1/3
# beta = 1/3
# # ############## MODULO DE DEMANDA #############
# m = matrixod(n, y=y, a=a, alpha=alpha, beta=beta)
# print(m.text)
# if m.plot:
#     print("Informacion de demanda")
#     print(m.matrix)
# ############CREACION DE ARCHIVOS CSV##############
# c.nodes.to_csv(dir_out + "\\nodes.txt", index=False)
# c.edges.to_csv(dir_out + "\\arc.txt", index=False)
#
#
#
# # texto gráficos
# if c.plot:
#     t1 = "n:{}, L:{}, g:{}".format(n, L, g)
#     t2 = "etha:{}, etha_zone:{}".format(etha, etha_zone)
#     t3 = "angles: {}".format(angles)
#     t4 = "Gi:{}, Hi:{}".format(Gi, Hi)
#     plot_city(c.nodes, c.edges, t1, t2, t3, t4)

from sidermit.city import graph
from sidermit.publictransportsystem import TransportNetwork, TransportModeManager, TransportMode, Passenger
from sidermit.extended_graph import ExtendedGraph
from sidermit.hyper_path import Hyperpath

graph_obj = graph.Graph.build_from_parameters(n=5, l=1000, g=0.5, p=2)

mode_manager = TransportModeManager()
bus_obj = mode_manager.get_mode("bus")
metro_obj = mode_manager.get_mode("metro")

passenger_obj = Passenger.get_default_passenger()

network = TransportNetwork(graph_obj)

feeder_routes = network.get_feeder_routes(bus_obj)
radial_routes = network.get_radial_routes(metro_obj)
radial_routes_bus = network.get_radial_routes(bus_obj)
circular_routes = network.get_circular_routes(bus_obj)

for route in feeder_routes:
    network.add_route(route)

for route in radial_routes:
    network.add_route(route)

for route in circular_routes:
    network.add_route(route)

for route in radial_routes_bus:
    network.add_route(route)

extended_graph = ExtendedGraph(graph_obj, network, passenger_obj)

print(extended_graph.__str__())
# extended_graph_nodes = extended_graph.get_extended_graph_nodes()
# extended_graph_edges = extended_graph.get_extended_graph_edges()

# print(extended_graph.__str__())

hyperpath_obj= Hyperpath()

successor, successor_inf, labels, labels_inf, frequencies = hyperpath_obj.get_hyperpath(extended_graph, "1", "0")

print(hyperpath_obj.__str__(successor, successor_inf, labels, labels_inf, frequencies))

# city_nodes = ExtendedGraph.build_city_nodes(graph_obj)
# tree_graph = ExtendedGraph.build_tree_graph(network, city_nodes)
# stop_nodes = ExtendedGraph.build_stop_nodes(tree_graph)
# route_nodes = ExtendedGraph.build_route_nodes(network, stop_nodes)
#
# access_edges = ExtendedGraph.build_access_edges(extended_graph_nodes)
# boarding_edges = ExtendedGraph.build_boarding_edges(extended_graph_nodes, 28)
# alighting_edges = ExtendedGraph.build_alighting_edges(extended_graph_nodes, passenger_obj)
# route_edges = ExtendedGraph.build_route_edges(extended_graph_nodes)


# for edge in route_edges:
#     print("{} - {} - {} - {} - {} - {}".format(edge.nodei.id, edge.nodei.route.id, edge.nodei.direction, edge.nodei.stop_node.city_node.graph_node.name, edge.nodej.stop_node.city_node.graph_node.name, edge.t))

# for city_node in extended_graph_nodes:
#     print("City node\n-Graph node name: {}".format(city_node.graph_node.name))
#
#     for stop_node in extended_graph_nodes[city_node]:
#
#         # information about access edge
#         for edge in extended_graph_edges:
#             if edge.nodei == city_node and edge.nodej == stop_node:
#                 print("\tAccess edge\n\t-Access time: {} [min]".format(edge.t))
#
#         print("\t\tStop node\n\t\t-Mode name: {}".format(stop_node.mode.name))
#
#         for route_node in extended_graph_nodes[city_node][stop_node]:
#
#             # information about boarding edge
#             for edge in extended_graph_edges:
#                 if edge.nodei == stop_node and edge.nodej == route_node:
#                     print("\t\t\tBoarding edge\n\t\t\t-Frequency: {} [veh/h]".format(edge.f))
#
#             # information about boarding edge
#             for edge in extended_graph_edges:
#                 if edge.nodei == route_node and edge.nodej == stop_node:
#                     print("\t\t\tAlighting edge\n\t\t\t-Penalty transfer: {} [min]".format(edge.t))
#
#             # information about route node
#             if route_node.prev_route_node is None:
#                 print(
#                     "\t\t\t\tRoute node\n\t\t\t\t-Route_id: {}\n\t\t\t\t-Direction: {}\n\t\t\t\t-Previous stop: {}\n\t\t\t\t-Time to previous stop: {} [min]".format(
#                         route_node.route.id,
#                         route_node.direction, "no data", 0))
#             else:
#                 t = 0
#                 for edge in extended_graph_edges:
#                     if edge.nodei == route_node.prev_route_node and edge.nodej == route_node:
#                         t = edge.t
#                         break
#                 print(
#                     "\t\t\t\tRoute node\n\t\t\t\t-Route_id: {}\n\t\t\t\t-Direction: {}\n\t\t\t\t-Previous stop: {}\n\t\t\t\t-Time to previous stop: {} [min]".format(
#                         route_node.route.id,
#                         route_node.direction,
#                         route_node.prev_route_node.stop_node.city_node.graph_node.name,
#                         t))
