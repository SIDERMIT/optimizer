import pandas as pd

# class to build transit network
class transit_network:
    # asumimos que la ciudad cumple estandares de contruccion de ciudad asimetrica y simetrica
    def __init__(self, info_nodes, info_edge, n):
        self.info_nodes = info_nodes
        self.info_edge = info_edge
        self.n = n

        self.network = pd.DataFrame()
        self.network["route_id"] = []
        self.network["route_name"] = []
        self.network["direction_id"] = []
        self.network["stop_sequences"] = []
        self.network["route_type"] = []

        # numero de rutas
        self.n_routes = 0

    # verificamos que arco exista
    def check_edge(self, i, j):
        if len(self.info_edge[self.info_edge["nodei"]==i])>=1:
            info_filter = self.info_edge[self.info_edge["nodei"]==i]
            if len(info_filter[info_filter["nodej"]==j])>=1:
                return True
        return False
    # add cir
    def add_cir(self, direction_id, route_type, route_name = None):

        if self.n > 1:

            route_id = self.n_routes
            self.n_routes = self.n_routes +1
            if route_name is None:
                route_name = "CIR_{}".format(route_id)
            stop_sequences = []

            for z in range(self.n):
                zone = z + 1
                nodei = 2*(zone-1)+2
                if z == self.n -1:
                    nodej = 2
                else:
                    nodej =  2*(zone)+2

                if self.check_edge(nodei, nodej):# arco existe
                    if nodei == 2:
                        stop_sequences.append(2)
                        stop_sequences.append(nodej)
                    else:
                        stop_sequences.append(nodej)
                else:
                    print("Error transit_network: arco {}, {} no existe en city_graph".format(nodei, nodej))

            df = pd.DataFrame()
            df["route_id"] = route_id
            df["route_name"] = route_name
            df["direction_id"] = direction_id
            df["stop_sequences"] = "{}".format(stop_sequences)
            df["route_type"] = route_type

            print(stop_sequences)

            self.network = pd.compat([self.network, df], ignore_index=True)

        else:
            print("Warning transit_network: para agregr CIR se necesitan mas de 2 zonas")

