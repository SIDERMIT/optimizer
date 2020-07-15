from scipy.optimize import minimize
import matplotlib.pyplot as plt
import numpy as np


def fun(x) :
    return (x[0] - 1)**2 + (x[1] - 2.5)**2 # paraboloid centered at (1, 2.5)

# Define constrains, as inequalities
# the first one, for instance, implies that : x - 2y + 2 > 0
cons = ({'type': 'ineq', 'fun': lambda x:  x[0] - 2 * x[1] + 2},
        {'type': 'ineq', 'fun': lambda x: -x[0] - 2 * x[1] + 6},
        {'type': 'ineq', 'fun': lambda x: -x[0] + 2 * x[1] + 2})

# define bounds: in tis case, all variables are positive
bnds = ((0, None), (0, None))

# solve using the SLSQP method
res = minimize(fun, (2, 0), method='SLSQP', bounds=bnds, constraints=cons)

print(res)

fig, ax = plt.subplots(figsize=(8, 6))
x_ = np.linspace(-2, 4, 100)  # Creating 1D arrays between -4 and 4 for x an y
y_ = np.linspace(0, 5, 100)  # Creating 1D arrays between -4 and 4 for x an y
X, Y = np.meshgrid(x_, y_)  # With this comand we create a 100x100 2D mesh
# We create the figure and also give it an alias to change its attributes
c = ax.contour(X, Y, fun([X, Y]), 20, cmap='viridis') # The 50 is the number of countour lines
ax.set_xlabel(r"$x_1$", fontsize=18)  # we set the x label
ax.set_ylabel(r"$x_2$", fontsize=18)  # we set the y label
plt.colorbar(c, ax=ax)                # We add a colorbar

ax.plot(res.x[0], res.x[1], 'r*', markersize=15)

plt.show()


