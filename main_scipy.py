import numpy as np
from scipy.optimize import minimize, NonlinearConstraint

from sidermit.city import Graph, Demand
from sidermit.optimization import Optimizer
from sidermit.publictransportsystem import Passenger, TransportMode
from sidermit.publictransportsystem import TransportNetwork

graph_obj = Graph.build_from_parameters(2, 10, 0.5, 2)
demand_obj = Demand.build_from_parameters(graph_obj, 100, 0.5, 1 / 3, 1 / 3)
passenger_obj = Passenger.get_default_passenger()
[bus_obj, metro_obj] = TransportMode.get_default_modes()
network_obj = TransportNetwork(graph_obj)

feeder_bus = network_obj.get_feeder_routes(bus_obj)
radial_metro = network_obj.get_radial_routes(metro_obj, short=True)

for route in feeder_bus:
    network_obj.add_route(route)
for route in radial_metro:
    network_obj.add_route(route)

opt = Optimizer(graph_obj, demand_obj, passenger_obj, network_obj)
fo = opt.f_opt


def fun(fopt):
    print("f: {}".format(fopt))
    print("VRC: {}".format(opt.VRC(fopt)))
    return opt.VRC(fopt)


def con(fopt):
    ineq_k, ineq_f = opt.get_constrains(fopt)
    con = []
    for c in ineq_k:
        con.append(c)
    for c in ineq_f:
        con.append(c)
    return con


constr_func = lambda fopt: np.array(con(fopt))

nonlin_con = NonlinearConstraint(constr_func, 0., np.inf)

from scipy.optimize import Bounds

bounds = Bounds([0, 0, 0, 0], [float('inf'), float('inf'), float('inf'), float('inf')])

res = minimize(fun, fo, method='trust-constr', constraints=nonlin_con, tol=0.2, bounds=bounds)

print(res)
