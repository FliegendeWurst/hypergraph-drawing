#! /usr/bin/env python3

import sys
import itertools
import pydot # tested with 1.4.2

if len(sys.argv) != 2:
    print("Usage: dot_hypergraph_to_asymptote.py <dot file>")
    sys.exit(1)

# output size
width = None # 400
height = 639

# size of node and edge labels
fontsize = "20pt"

# specify minimum text width
# (useful if your labels contain wide unicode characters)
text_width_base = 35 # 40
text_width_factor = 5.5 # 9

# draw edges reversed
reverse_edges = True

# output \begin{asy} ... \end{asy}
output_latex = False

graphs = pydot.graph_from_dot_file(sys.argv[1])
graph = graphs[0]

nodes = dict()
node_list = []

for node in graph.get_nodes():
    pos = node.get_pos()
    if pos is None:
        continue
    pos = pos[1:-1]
    nodes[node.get_name()] = tuple(map(float, pos.split(",")))
    node_list.append(node.get_name())

edges = dict()

for edge in graph.get_edges():
    label = edge.get_label()
    if label is None:
        continue
    label = label.replace('"', "")
    src = edge.get_source()
    dest = edge.get_destination()
    if label not in edges:
        edges[label] = [(src, dest)]
    else:
        edges[label].append((src, dest))

hyperedges = []

for label in edges:
    xmin = min(itertools.chain(*map(lambda x: [nodes[x[0]][0], nodes[x[1]][0]], edges[label])))
    xmax = max(itertools.chain(*map(lambda x: [nodes[x[0]][0], nodes[x[1]][0]], edges[label])))
    ymin = min(map(lambda x: nodes[x[0]][1], edges[label]))
    ymax = max(map(lambda x: nodes[x[1]][1], edges[label]))
    x = (xmax + xmin) / 2
    y = (ymax + ymin) / 2
    #print(label, xmin, xmax, ymin, ymax, x, y)
    hyperedges.append(((x, y), label))
#input("")

if output_latex:
    print("\\begin{asy}")

# code based on https://tex.stackexchange.com/a/108099/185782 (g.kov)

if width is None:
    width = 0
if height is None:
    height = 0
print("size(", width, ",", height, ");")
print("import flowchart;")
if fontsize is not None:
    print("defaultpen(fontsize(", fontsize, "));")

print("pair[]pv={")

for node in node_list:
    print(nodes[node], ",")

print("};")

print("string[]pv_labels={")

for name in node_list:
    if not name.startswith('"'):
        name = '"' + name
    if not name[-1] == '"':
        name = name + '"'
    print(name, ',')

print("};")

print("real[]pv_size={")

for node in node_list:
    print(text_width_base + len(node[1:-1])*text_width_factor, ',')

print("};")

print("pair[][] pe={")

for x in hyperedges:
    print("{", x[0], ",E},")

print("};")

print("string[] pe_labels={")

for x in hyperedges:
    print('"', x[1].replace("_", "\\_"), '",')

print("};")

print("""
pen nodeFill=white;
pen nodeLine=darkblue+1.2pt+opacity(0.5);

block[] v=new block[pv.length];
block[] e=new block[pe.length];


for(int i=0;i<pv.length;++i){
  v[i]=rectangle(pv_labels[i],pv[i],nodeFill,nodeLine,minwidth=pv_size[i]);
  draw(v[i]);
}

string s;
for(int i=0;i<pe.length;++i){
  s=pe_labels[i];
  e[i]=circle(s,pe[i][0]);
  label(s,pe[i][0],pe[i][1]);
  dot(pe[i][0]);
}

add(
  new void(picture pic, transform t) {
    blockconnector operator --=blockconnector(pic,t);
    real tg;
     pen linePen=darkblue+1.2pt;
     currentpen=linePen;
     arrowfactor=4;
""")

for n, edge in enumerate(hyperedges):
    label = edge[1]
    for e in edges[label]:
        i1 = node_list.index(e[0])
        i2 = node_list.index(e[1])
        if reverse_edges:
            print("tg=90;")
            print("draw(pic,v[%d].top(t){dir(90)} .. {dir(tg)}t*e[%d].center{dir(tg)} .. v[%d].bottom(t){dir(90)}, Arrow(HookHead));" % (i2, n, i1))
        else:
            print("tg=270;")
            print("draw(pic,v[%d].bottom(t){dir(270)} .. {dir(tg)}t*e[%d].center{dir(tg)} .. v[%d].top(t){dir(270)},Arrow(HookHead));" % (i1, n, i2))

print("});")
if output_latex:
    print("\\end{asy}")
