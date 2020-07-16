from scipy.optimize import minimize, NonlinearConstraint, SR1
import matplotlib.pyplot as plt
import numpy as np
import math

def f(x):
    return math.log(x[0] ** 2 + 1) + x[1] ** 4 + x[0] * x[2]


constr_func = lambda x: np.array([x[0] ** 3 - x[1] ** 2 - 1,
                                  x[0],
                                  x[2]])

x0 = [1., 1., 1.]

nonlin_con = NonlinearConstraint(constr_func, 0., np.inf)

res = minimize(f, x0, method='SLSQP', constraints = nonlin_con)

print(res)
