import numpy as np
from scipy.optimize import minimize, NonlinearConstraint

from sidermit.city import Graph, Demand
from sidermit.optimization import Optimizer
from sidermit.publictransportsystem import Passenger, TransportMode
from sidermit.publictransportsystem import TransportNetwork

graph_obj = Graph.build_from_parameters(8, 10, 0.85, 2)
demand_obj = Demand.build_from_parameters(graph_obj, 100000, 0.78, 1 / 4, 0.22)
passenger_obj = Passenger.get_default_passenger()
[bus_obj, metro_obj] = TransportMode.get_default_modes()
network_obj = TransportNetwork(graph_obj)

diametral_larga4 = network_obj.get_diametral_routes(bus_obj, 4)
diametral_larga3 = network_obj.get_diametral_routes(bus_obj, 3)
tangencial_larga1 = network_obj.get_tangencial_routes(bus_obj, 1)
tangencial_larga2 = network_obj.get_tangencial_routes(bus_obj, 2)
radial = network_obj.get_radial_routes(bus_obj)
alimentadora = network_obj.get_feeder_routes(bus_obj)
radialc = network_obj.get_radial_routes(bus_obj, short=True)
diametral_corta4 = network_obj.get_diametral_routes(bus_obj, 4, short=True)
diametral_corta3 = network_obj.get_diametral_routes(bus_obj, 3, short=True)
diametral_corta2 = network_obj.get_diametral_routes(bus_obj, 2, short=True)
tangencial_corta1 = network_obj.get_tangencial_routes(bus_obj, 1, short=True)
tangencial_corta2 = network_obj.get_tangencial_routes(bus_obj, 2, short=True)

routes = [diametral_larga4, diametral_larga3, tangencial_larga1, tangencial_larga2, radial, alimentadora, radialc,
          diametral_corta4, diametral_corta3, diametral_corta2, tangencial_corta1, tangencial_corta2]

routes = [alimentadora, radialc]

for route_type in routes:
    for route in route_type:
        network_obj.add_route(route)

# podemos agregar numero de iteraciones
opt_obj = Optimizer(graph_obj, demand_obj, passenger_obj, network_obj, f=None)
res = opt_obj.network_optimization(graph_obj, demand_obj, passenger_obj, network_obj, f=None, tolerance=0.01)
print(opt_obj.string_overall_results(opt_obj.overall_results(res)))
network_results = opt_obj.network_results(res)
print(opt_obj.string_network_results(network_results))
# print(list_res)


# graph_obj = Graph.build_from_parameters(8, 10, 0.5, 2)
# demand_obj = Demand.build_from_parameters(graph_obj, 100000, 0.5, 1 / 3, 1 / 3)
# passenger_obj = Passenger.get_default_passenger()
# [bus_obj, metro_obj] = TransportMode.get_default_modes()
# network_obj = TransportNetwork(graph_obj)
#
# feeder_bus = network_obj.get_feeder_routes(bus_obj)
# radial_metro = network_obj.get_radial_routes(metro_obj, short=True)
#
# for route in feeder_bus:
#     network_obj.add_route(route)
# for route in radial_metro:
#     network_obj.add_route(route)
#
# opt = Optimizer(graph_obj, demand_obj, passenger_obj, network_obj, f=None)
# fo = opt.f_opt
#
#
# def fun(fopt):
#     print("f: {}".format(fopt))
#     print("VRC: {}".format(opt.VRC(fopt)))
#     return opt.VRC(fopt)
#
#
# def con(fopt):
#     ineq_k, ineq_f = opt.get_constrains(fopt)
#     con = []
#     for c in ineq_k:
#         con.append(c)
#     for c in ineq_f:
#         con.append(c)
#     return con
#
#
# constr_func = lambda fopt: np.array(con(fopt))
#
# lb = [-1 * np.inf] * 112
# ub = [0] * 112
# nonlin_con = NonlinearConstraint(constr_func, lb=lb, ub=ub)
#
# from scipy.optimize import Bounds
#
# bounds = Bounds(lb=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#                 ub=[np.inf, np.inf, np.inf, np.inf, np.inf, np.inf, np.inf, np.inf, np.inf, np.inf, np.inf, np.inf,
#                     np.inf, np.inf, np.inf, np.inf])
#
# res = minimize(fun, fo, method='trust-constr', constraints=nonlin_con, tol=0.2, bounds=bounds)
#
# print(res)
