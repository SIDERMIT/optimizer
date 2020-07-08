from sidermit.city import graph
from sidermit.publictransportsystem import Route, TransportNetwork, TransportModeManager, Passenger, TransportMode
from sidermit.preoptimization import ExtendedGraph
from sidermit.preoptimization import Hyperpath
from collections import defaultdict

# graph_obj = graph.Graph.build_from_parameters(n=2, l=5000, g=2, p=2, Hi=[(70 / 6 + 5) / 15, 1], angles=[10, 190])
# graph_obj.plot("sidermit.png")
#
# mode_1 = TransportMode("mode_1", 1, 1, 1, 1, 76, 0, 100, 100, 1, 0, 1)  # 25
# mode_3 = TransportMode("mode_3", 1, 1, 1, 1, 150, 0, 100, 100, 1, 0, 1)  # 4 - 4
# mode_4 = TransportMode("mode_4", 1, 1, 1, 1, 60, 0, 100, 100, 1, 0, 1)  # 10
#
# passenger = Passenger(1, 1, 1, 0, 0, 1, 1, 0, 0)
#
# line_1 = Route("line_1", mode_1, "1,2,0,4,3", "3,4,0,2,1", "1,3", "3,1")
# line_2 = Route("line_2", mode_1, "1,2,0,4", "4,0,2,1", "1,2,4", "4,2,1")
# line_3 = Route("line_3", mode_3, "2,0,4,3", "3,4,0,2", "2,4,3", "3,4,2")
# line_4 = Route("line_4", mode_4, "4,3", "3,4", "4,3", "3,4")
#
# network = TransportNetwork(graph_obj)
# network.add_route(line_1)
# network.add_route(line_2)
# network.add_route(line_3)
# network.add_route(line_4)
#
# frequency = defaultdict(float)
# frequency["line_1"] = 10
# frequency["line_2"] = 10
# frequency["line_3"] = 4
# frequency["line_4"] = 20
#
# extended_graph = ExtendedGraph(graph_obj, network.get_routes(), passenger.spt, frequency)
# print(extended_graph.__str__())
#
# # para obtener un par OD para algoritmos que vienen
# extended_graph_nodes = extended_graph.get_extended_graph_nodes()
# P1 = None
# P2 = None
# for city_node in extended_graph_nodes:
#     if str(city_node.graph_node.name) == "P_2":
#         P2 = city_node
#     if str(city_node.graph_node.name) == "P_1":
#         P1 = city_node
#
# # generamos hiperruta para un par de nodos de origen y destino
# hyperpath_obj = Hyperpath(extended_graph, passenger)
# successors, label, frequencies = hyperpath_obj.build_hyperpath_graph(P1, P2)
# print(hyperpath_obj.string_hyperpath_graph(successors, label, frequencies))
#
# # obtenemos hiperrutas
# hyperpath_OD = hyperpath_obj.get_hyperpath_OD(P1, P2)
# string_HP_OD = hyperpath_obj.string_hyperpaths_OD(hyperpath_OD, label)
# print(string_HP_OD)
#
# hyperpath_obj.plot(hyperpath_OD)



graph_obj = graph.Graph.build_from_parameters(n=2, l=10000, g=0.5, p=2)

mode_manager = TransportModeManager()
bus_obj = mode_manager.get_mode("bus")
metro_obj = mode_manager.get_mode("metro")

passenger_obj = Passenger.get_default_passenger()
# para cambiar penalidad de transbordo
passenger_obj.spt = 0

network = TransportNetwork(graph_obj)

# agregamos rutas a la red
feeder_routes = network.get_feeder_routes(bus_obj)
radial_routes = network.get_radial_routes(metro_obj, short=True)
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

# generamos grafo extendido
extended_graph = ExtendedGraph(graph_obj, network.get_routes(), passenger_obj.spt)
print(extended_graph.__str__())

# para obtener un par OD para algoritmos que vienen
extended_graph_nodes = extended_graph.get_extended_graph_nodes()
P1 = None
CBD = None
for city_node in extended_graph_nodes:
    if str(city_node.graph_node.name) == "CBD":
        CBD = city_node
    if str(city_node.graph_node.name) == "P_1":
        P1 = city_node

# generamos hiperruta para un par de nodos de origen y destino
hyperpath_obj = Hyperpath(extended_graph, passenger_obj)
successors, label, frequencies = hyperpath_obj.build_hyperpath_graph(P1, CBD)
print(hyperpath_obj.string_hyperpath_graph(successors, label, frequencies))

# obtenemos hiperrutas
hyperpath_OD = hyperpath_obj.get_hyperpath_OD(P1, CBD)
string_HP_OD = hyperpath_obj.string_hyperpaths_OD(hyperpath_OD, label)
print(string_HP_OD)

print("Penalidad de transbordo: {} [min]".format(passenger_obj.spt))

hyperpath_obj.plot(hyperpath_OD)
