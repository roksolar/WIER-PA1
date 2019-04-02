import networkx as nx
import matplotlib.pyplot as plt
import psycopg2
from scipy import sparse
import time
start = time.time()
conn = psycopg2.connect("host='localhost' dbname='postgres2' user='postgres2' password='test2'")
cur = conn.cursor()
sql = '''select from_page,to_page,p1.page_type_code, p2.page_type_code from crawldb.link l, crawldb.page p1, crawldb.page p2 
where l.from_page=p1.id and l.to_page=p2.id and l.to_page 
in (select id from crawldb.page where page_type_code != 'FRONTIER')
'''



cur.execute(sql)
conn.commit()
a = cur.fetchall()
cur.close()

G = nx.Graph()
edges = []
color_map = []
for source, end, type1, type2 in a:

    edges.append((source,end))
    if type1 == "HTML":

        if source not in G.nodes:
            color_map.append("green")
            G.add_node(source,  node_size=3, width=0.5)
    elif type1 == "BINARY":

        if source not in G.nodes:
            color_map.append("blue")
            G.add_node(source,  node_size=3, width=0.5)
    elif type1 == "DUPLICATE":

        if source not in G.nodes:
            color_map.append("yellow")
            G.add_node(source,  node_size=3, width=0.5)
    elif type1 == "TIMEOUT":

        if source not in G.nodes:
            color_map.append("red")
            G.add_node(source,  node_size=3, width=0.5)

    if type2 == "HTML":
        if end not in G.nodes:
            color_map.append("green")
            G.add_node(end,  node_size=3, width=0.5)
    elif type2 == "BINARY":
        if end not in G.nodes:
            color_map.append("blue")
            G.add_node(end,  node_size=3, width=0.5)
    elif type2 == "DUPLICATE":
        if end not in G.nodes:
            color_map.append("yellow")
            G.add_node(end,  node_size=3, width=0.5)
    elif type2 == "TIMEOUT":
        if end not in G.nodes:
            color_map.append("red")
            G.add_node(end, node_size=3, width=0.5)


print("Podatki prebrani...")
#for x,y in edges:
#    G.add_edge(x,y)
G.add_edges_from(edges)
#nx.draw(G, node_size=1, width=0.5)
nx.draw(G, node_color = color_map,  node_size=7, width=0.5)
print("nx draw končan...")
end = time.time()
print(end-start)
plt.show()


#TODO: NA NOVO ODDAJ VIZUALIZACIJO!!!!!!!!!!!!!!!!!!!!!!!!!!!
