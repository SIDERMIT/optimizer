from scipy.optimize import minimize, NonlinearConstraint
import numpy as np
import math

def f(x):
    return math.log(x[0] ** 2 + 1) + x[1] ** 4 + x[0] * x[2]

def con1(x):
    return x[0] ** 3 - x[1] ** 2 - 1

def con2(x):
    return x[0]

def con3(x):
    return x[2]

def con(x):
    return [con1(x), con2(x), con3(x)]

constr_func = lambda x: np.array(con(x))

x0 = [1., 1., 1.]

nonlin_con = NonlinearConstraint(constr_func, 0., np.inf)

res = minimize(f, x0, method='SLSQP', constraints = nonlin_con)

print(res)
