import pymel.core as pm

from lib import attributes

from importlib import reload
reload(attributes)


class Network:
    def __init__(self, node=None):
        self.name = None
        self.node = None

        if node:
            self.node = pm.PyNode(node)

    def build(self, name):
        self.name = name
        if pm.objExists(self.name):
            self.node = pm.PyNode(self.name)
        else:
            self.node = pm.createNode('network', n=self.name)
            part = name.split('_')[0]
            attributes.add_tag(self.node, 'FACE', name, "01", 'None', part)

    def add_attr(self, attr_name):
        pm.addAttr(self.node, ln=attr_name, type='message')

    def remove_attr(self, attr_name):
        pm.deleteAttr('{}.{}'.format(self.node, attr_name))

    def get_connection(self, attr_name):
        return pm.listConnections(self.node + '.' + attr_name)[0]

    def set_connection(self, obj, attr_name):
        pm.connectAttr(obj.message, self.node + '.' + attr_name, f=1)

    def get_all_connections(self):
        connections = []
        for attr in self.node.listAttr():
            if attr.type() == 'message':
                if attr.connections():
                    connections.append(attr.connections()[0])
        return connections

    def select_all(self):
        items = self.get_all_connections()
        pm.select(items)

    def select(self, item):
        node = self.get_connection(item)
        pm.select(node)

    def select_side(self, side):
        items = self.get_all_connections()
        nodes = []
        for each in items:
            if each.name().startswith(side):
                nodes.append(each)
        pm.select(nodes)

    def get_bind_joints(self):
        controls = self.get_all_connections()
        binds = []
        for each in controls:
            node = pm.PyNode(each.replace('_ctrl', '_bind'))
            binds.append(node)

