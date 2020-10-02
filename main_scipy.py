from sidermit.city import Graph, Demand
from sidermit.optimization import Optimizer
from sidermit.publictransportsystem import Passenger, TransportMode
from sidermit.publictransportsystem import TransportNetwork

# build city graph
graph_obj = Graph.build_from_parameters(5, 10, 0.85, 2)
# build demand
demand_obj = Demand.build_from_parameters(graph_obj, 100000, 0.78, 1 / 4, 0.22)
# build passenger
passenger_obj = Passenger.get_default_passenger()
# build transport modes
[bus_obj, metro_obj] = TransportMode.get_default_modes()
# build transport network empty
network_obj = TransportNetwork(graph_obj)

# to build routes
# diametral_larga4 = network_obj.get_diametral_routes(bus_obj, 4)
# diametral_larga3 = network_obj.get_diametral_routes(bus_obj, 3)
# tangencial_larga1 = network_obj.get_tangencial_routes(bus_obj, 1)
# tangencial_larga2 = network_obj.get_tangencial_routes(bus_obj, 2)
radial = network_obj.get_radial_routes(bus_obj)
alimentadora = network_obj.get_feeder_routes(bus_obj)
radialc = network_obj.get_radial_routes(bus_obj, short=True)
# diametral_corta4 = network_obj.get_diametral_routes(bus_obj, 4, short=True)
# diametral_corta3 = network_obj.get_diametral_routes(bus_obj, 3, short=True)
# diametral_corta2 = network_obj.get_diametral_routes(bus_obj, 2, short=True)
# tangencial_corta1 = network_obj.get_tangencial_routes(bus_obj, 1, short=True)
# tangencial_corta2 = network_obj.get_tangencial_routes(bus_obj, 2, short=True)
circular = network_obj.get_circular_routes(metro_obj)

# add routes in transport network
routes = [alimentadora, radial, circular]
for route_type in routes:
    for route in route_type:
        network_obj.add_route(route)

# build optimizer object
opt_obj = Optimizer(graph_obj, demand_obj, passenger_obj, network_obj, f=None)
# run optimizer
res = Optimizer.network_optimization(graph_obj, demand_obj, passenger_obj, network_obj, f=None, tolerance=0.01)

# get overall results
ov_results = opt_obj.overall_results(res)
print(opt_obj.string_overall_results(ov_results))
# get transport network results
network_results = opt_obj.network_results(res)
print(opt_obj.string_network_results(network_results))

# to write network results
opt_obj.write_file_network_results("output.csv", network_results)
