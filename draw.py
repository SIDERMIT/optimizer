from matplotlib import pyplot as plt


def plot_city(info_nodes, info_edge, t1, t2, t3, t4):
    info_cbd = info_nodes[info_nodes["tipo"] == "CBD"]
    info_sc = info_nodes[info_nodes["tipo"] == "SC"]
    info_p = info_nodes[info_nodes["tipo"] == "P"]

    # coordenadas nodos CBd, SC y P
    x_cbd = info_cbd["x"]
    y_cbd = info_cbd["y"]
    x_sc = info_sc["x"]
    y_sc = info_sc["y"]
    x_p = info_p["x"]
    y_p = info_p["y"]

    # ploteamos arcos
    for line in range(len(info_edge)):
        x = [info_edge.at[line, "x_i"], info_edge.at[line, "x_j"]]
        y = [info_edge.at[line, "y_i"], info_edge.at[line, "y_j"]]
        plt.plot(x, y, color="lime")

    # ploteamos nodos
    plt.plot(x_p, y_p, 'ro')
    plt.plot(x_sc, y_sc, 'bo')
    plt.plot(x_cbd, y_cbd, 'mo')

    # propiedades gráfico
    plt.title("City graph {}{}{}{}{}{}{}{}".format("\n", t1, "\n", t2, "\n", t3, "\n", t4))
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.gca().set_aspect('equal')
    plt.grid()
    plt.show()
