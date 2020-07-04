from sidermit.city import graph
from sidermit.publictransportsystem import TransportNetwork, TransportModeManager, TransportMode, Passenger
from sidermit.extended_graph import ExtendedGraph
from sidermit.hyper_path import Hyperpath

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

# generamos grafo extendido
extended_graph = ExtendedGraph(graph_obj, network, passenger_obj)
print(extended_graph.__str__())
extended_graph_nodes = extended_graph.get_extended_graph_nodes()

P1 = None
CBD = None
for city_node in extended_graph_nodes:
    if str(city_node.graph_node.name) == "CBD":
        CBD = city_node
    if str(city_node.graph_node.name) == "P_1":
        P1 = city_node

# generamos hiperruta para un par de nodos de origen y destino
hyperpath_obj = Hyperpath()
successors, label, frequencies = hyperpath_obj.build_hyperpath(extended_graph, P1, CBD)
print(hyperpath_obj.__str__(successors, label, frequencies))

# obtenemos hiperrutas
HP = hyperpath_obj.get_hyper_routes(extended_graph, P1, CBD)
string_HP = hyperpath_obj.string_hyperpaths(HP)
print(string_HP)

print("Penalidad de transbordo: {} [min]".format(passenger_obj.spt))

