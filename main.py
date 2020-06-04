from matrixod import matrixod
from city_graph import city_graph
from draw import plot_city
from transit_network import transit_network

dir_out = r"C:\Users\felip\Downloads\esteb\output"
# path = r"C:\Users\felip\Downloads\esteb\inputs\matriz.txt"

############## PARAMETROS DE CIUDAD #############
n = 8
L = 10000
g = 0.5
p = 2
etha = 1
etha_zone = 3
angles = [10, 60, 150, 160, 180, 240, 250, 355]
Gi = [0.5, 1, 0.5, 1, 0.5, 1, 0.5, 1]
Hi = [1, 2, 1, 2, 1, 2, 1, 2]
############## MODULO DE CIUDAD #############
# falta definir integracion de informacion de nodes y arcos
# validacion de archivos externos
# validacion geométrica de parámetros
c = city_graph(n, L=L, g=g, etha=etha, etha_zone=etha_zone, angles=angles, Gi=Gi, Hi=Hi)
print(c.text_parameters)
if c.plot:
    print("Informacion de nodos")
    print(c.nodes)
    print("Informacion de nodos")
    print(c.edges)
# ############## PARAMETROS DE DEMANDA #############
y = 1000
a = 0.5
alpha = 1/3
beta = 1/3
# ############## MODULO DE DEMANDA #############
m = matrixod(n, y=y, a=a, alpha=alpha, beta=beta)
print(m.text)
if m.plot:
    print("Informacion de demanda")
    print(m.matrix)
############CREACION DE ARCHIVOS CSV##############
c.nodes.to_csv(dir_out + "\\nodes.txt", index=False)
c.edges.to_csv(dir_out + "\\arc.txt", index=False)



# texto gráficos
if c.plot:
    t1 = "n:{}, L:{}, g:{}".format(n, L, g)
    t2 = "etha:{}, etha_zone:{}".format(etha, etha_zone)
    t3 = "angles: {}".format(angles)
    t4 = "Gi:{}, Hi:{}".format(Gi, Hi)
    plot_city(c.nodes, c.edges, t1, t2, t3, t4)