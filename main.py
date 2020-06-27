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

graph_obj = graph.Graph.build_from_parameters(n=5, l=1000, g=0.5, p=2)
network = TransportNetwork(graph_obj)

mode_manager = TransportModeManager()
bus_obj = mode_manager.get_mode("bus")
metro_obj = mode_manager.get_mode("metro")
train_obj = TransportMode("train", 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1)

passenger_obj = Passenger(4, 2, 2, 2, 2, 2, 2, 2, 2)

feeder_routes = network.get_feeder_routes(bus_obj)
radial_routes = network.get_radial_routes(metro_obj)
circular_routes = network.get_circular_routes(train_obj)

for route in feeder_routes:
    network.add_route(route)

for route in radial_routes:
    network.add_route(route)

for route in circular_routes:
    network.add_route(route)

extended_graph = ExtendedGraph(graph_obj, network, passenger_obj)
extended_graph_nodes = extended_graph.get_extended_graph_nodes()

for city_node in extended_graph_nodes:
    print("City node: {}".format(city_node.graph_node.name))

    for stop_node in extended_graph_nodes[city_node]:
        print("Stop node: {}".format(stop_node.mode.name))

        for route_node in extended_graph_nodes[city_node][stop_node]:
            print("Route node: {}-{}, adj: {}".format(route_node.route.id,
                                                      route_node.direction, route_node.prev_route_node))
