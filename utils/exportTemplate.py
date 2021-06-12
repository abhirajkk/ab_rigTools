import os
import json
import pymel.core as pm
import sys
sys.path.append(r'F:\Development\ab_rigTools\Lib')
import network


def export(file_name, templates=[], path=None):
    data = {}
    for template in templates:
        template_inst = network.Network(template)
        template_nodes = template_inst.get_all_connections()
        nodes_data = {}
        for node in template_nodes:
            pos = pm.xform(node, q=1, t=1, ws=1)
            rot = pm.xform(node, q=1, rt=1, ws=1)
            nodes_data[node.name()] = {'pos': pos, 'rot': rot}
        data[template] = nodes_data
    file_name = os.path.join(path, '{}.{}'.format(file_name, 'json'))
    with open(file_name, 'w') as data_handle:
        json.dump(data, data_handle, indent=4)
    print ("template export done !!!", path)
