"""
author : abhiraj KK - abhiajk@gmail.com
version : 0.1
date : 13-08-2019

base class to build controls and associated hierarchy setup for facial rig

"""

import maya.api.OpenMaya as om
import pymel.core as pm

from utils import utility
from lib import attributes

from importlib import reload

reload(attributes)


class Control:
    def __init__(self, modules, version, side, part):
        self.modules = modules
        self.version = version
        self.side = side
        self.part = part
        self.override_color = self.set_color(side)

        self.hierarchy = ['zro', 'con', 'ort', 'mir', 'piv', 'ato', 'drn', 'ofs', 'nul']
        self.pre_hierarchy = ['zro', 'con', 'ort', 'mir', 'piv']
        self.attr_list = ['v']

        self.data = {}

        if pm.objExists('rig_grp'):
            self.top_grp = pm.PyNode('rig_grp')
        else:
            self.top_grp = pm.createNode('transform', n='rig_grp')

    @staticmethod
    def set_color(side):
        if side == 'L':
            color = 6
        elif side == 'R':
            color = 13
        else:
            color = 17
        return color

    @property
    def set_hierarchy_list(self):
        return self.hierarchy

    @set_hierarchy_list.setter
    def set_hierarchy_list(self, hierarchy):
        if isinstance(hierarchy, list):
            self.hierarchy = hierarchy
        else:
            return

    def get_node(self, suffix):
        return self.data.get(suffix, None)

    def build_selection(self, search='_loc', replace='_ctrl', hierarchy=True, pre=True):
        sel = pm.ls(sl=1)
        for each in sel:
            name = each.name().replace(search, replace)
            self.sphere(name, 1.0)
            name_obj = pm.PyNode(name)
            if hierarchy:
                self.set_hierarchy(name_obj)
                pm.matchTransform(name.replace('_ctrl', '_con'), each)
            if pre:
                self.set_pre_hierarchy(name_obj)
            self.set_limit_z()
            self.lock_attr()

    def build(self, item, search='_loc', replace='_ctrl', hierarchy=True, pre=True, bind=True):
        # sel = pm.ls(sl=1)
        name = item.name().replace(search, replace)
        self.sphere(name, 1.0)
        name_obj = pm.PyNode(name)
        if hierarchy:
            self.set_hierarchy(name_obj, bind=bind)
            # pm.matchTransform(name.replace('_ctrl', '_con'), item)
            pm.matchTransform(name + '_con', item)
        if pre:
            self.set_pre_hierarchy(name_obj)
        self.set_module_hierarchy(name, pre=pre, bind=bind)
        self.set_limit_z()
        self.lock_attr()

    def sphere(self, name, size):
        pts = [(0.5, 0.0, 0.0), (0.462, 0.0, 0.19), (0.35, 0.0, 0.35),
               (0.19, 0.0, 0.46), (0.0, 0.0, 0.5), (-0.19, 0.0, 0.46),
               (-0.35, 0.0, 0.35), (-0.46, 0.0, 0.19), (-0.5, 0.0, 0.0),
               (-0.46, 0.0, -0.19), (-0.35, 0.0, -0.35), (-0.19, 0.0, -0.46),
               (0.0, 0.0, -0.5), (0.19, 0.0, -0.46), (0.35, 0.0, -0.35),
               (0.46, 0.0, -0.19), (0.5, 0.0, 0.0), (0.46, -0.19, 0.0),
               (0.35, -0.35, 0.0), (0.19, -0.46, 0.0), (0.0, -0.5, 0.0),
               (-0.19, -0.46, 0.0), (-0.35, -0.35, 0.0), (-0.46, -0.19, 0.0),
               (-0.5, 0.0, 0.0), (-0.46, 0.19, 0.0), (-0.35, 0.35, 0.0),
               (-0.19, 0.46, 0.0), (0.0, 0.5, 0.0), (0.19, 0.46, 0.0),
               (0.35, 0.35, 0.0), (0.46, 0.19, 0.0), (0.5, 0.0, 0.0),
               (0.46, 0.0, 0.19), (0.35, 0.0, 0.35), (0.19, 0.0, 0.46),
               (0.0, 0.0, 0.5), (0.0, 0.24, 0.44), (0.0, 0.44, 0.24),
               (0.0, 0.5, 0.0), (0.0, 0.44, -0.24), (0.0, 0.24, -0.44),
               (0.0, 0.0, -0.5), (0.0, -0.24, -0.44), (0.0, -0.44, -0.24),
               (0.0, -0.5, 0.0), (0.0, -0.44, 0.24), (0.0, -0.24, 0.44),
               (0.0, 0.0, 0.5)]
        pts = [(y[0] * size, y[1] * size, y[2] * size) for y in pts]
        knots = range(len(pts))
        control = pm.curve(d=1, p=pts, k=knots, n=name)
        control.overrideEnabled.set(1)
        control.overrideColor.set(self.override_color)
        self.data['ctrl'] = control.name()
        self.add_tag(control)
        # return control

    def add_tag(self, obj):
        # component, modules, version, side, part
        attributes.add_tag(obj, 'FACE', self.modules, self.version, self.side, self.part)

    def set_hierarchy(self, obj, bind=True):
        # ctrl
        if obj.name().endswith('_ctrl'):
            name = obj.name().replace('_ctrl', '')
        else:
            name = obj.name()

        nodes = []
        for i in range(len(self.hierarchy)):
            # suffix = self.naming_data.get(self.hierarchy[i])
            suffix = self.hierarchy[i]
            node = pm.createNode('transform', n='{}_{}_{}'.format(name, 'ctrl', suffix))
            nodes.append(node)
            # self.data[self.hierarchy[i]] = node
            self.data[suffix] = node.name()

        for i in range(1, len(nodes) - 1):
            pm.parent(nodes[i], nodes[i - 1])

        pm.parent(nodes[-1], nodes[-2])

        pm.parent(obj, nodes[-2])

        obj.translate >> nodes[-1].translate
        obj.rotate >> nodes[-1].rotate
        obj.scale >> nodes[-1].scale

        # bind
        if bind:
            binds = []

            for i in range(len(self.hierarchy)):
                # suffix = self.naming_data.get(self.hierarchy[i], 'nul')
                suffix = self.hierarchy[i]
                node = pm.createNode('transform', n='{}_{}_{}'.format(name, 'bind', suffix))
                binds.append(node)
                # self.data[self.hierarchy[i]+'_bind'] = node
                self.data[suffix + '_bind'] = node.name()

            for i in range(1, len(binds) - 1):
                pm.parent(binds[i], binds[i - 1])

            bind_jnt = pm.createNode('joint', n=name + '_jnt')
            self.data['bind'] = bind_jnt.name()

            pm.parent(bind_jnt, self.data['nul_bind'])
            pm.parent(name + '_bind_nul', self.data['ofs_bind'])

            for each in self.hierarchy:
                src = pm.PyNode(self.data[each])
                tgt = pm.PyNode(self.data[each + '_bind'])
                src.translate >> tgt.translate
                src.rotate >> tgt.rotate
                src.scale >> tgt.scale

        if pm.objExists(self.modules + '_ctrl'):
            pm.parent(nodes[0], self.modules + '_ctrl')

        if pm.objExists(self.modules + '_bind'):
            pm.parent(binds[0], self.modules + '_bind')

        # return nodes[0], binds[0]

    def set_pre_hierarchy(self, obj, search='_ctrl'):
        grps = []
        for i, each in enumerate(self.pre_hierarchy):
            grp = pm.createNode('transform', n='{}'.format(obj.name().replace(search, '_pre_' + each)))
            self.data[each + '_pre'] = grp.name()
            pm.matchTransform(grp, obj)
            grps.append(grp)
            if i != 0:
                pm.parent(grp, grps[i - 1])

        # connect pre
        for pre in self.pre_hierarchy:
            src = pm.PyNode(self.data[pre])
            tgt = pm.PyNode(self.data[pre + '_pre'])
            src.translate >> tgt.translate
            src.rotate >> tgt.rotate
            src.scale >> tgt.scale

        if pm.objExists(self.modules + '_pre'):
            pm.parent(self.data['zro_pre'], self.modules + '_pre')


    @staticmethod
    def set_attribute(obj, attrs, **kwargs):
        for attr in attrs:
            pm.setAttr('{}.{}'.format(obj, attr), kwargs)

    def set_module_hierarchy(self, ctrl, pre=True, bind=True):

        module_ctrl = self.modules.lower() + '_ctrl'
        if not pm.objExists(module_ctrl):
            pm.createNode('transform', n=module_ctrl)
        if bind:
            module_bind = self.modules.lower() + '_bind'
            if not pm.objExists(module_bind):
                pm.createNode('transform', n=module_bind)
        if pre:
            module_pre = self.modules.lower() + '_pre'
            if not pm.objExists(module_pre):
                pm.createNode('transform', n=module_pre)

        ctrl_module = '{}_{}_{}'.format(self.side, self.modules.lower(), 'ctrls')
        bind_module = '{}_{}_{}'.format(self.side, self.modules.lower(), 'binds')
        pre_module = '{}_{}_{}'.format(self.side, self.modules.lower(), 'pres')
        # ctrl
        if pm.objExists(ctrl_module):
            pm.parent(self.data.get('zro'), ctrl_module)
        else:
            pm.createNode('transform', n=ctrl_module, p=module_ctrl)
            pm.parent(self.data.get('zro'), ctrl_module)
        # bind
        if bind:
            if pm.objExists(bind_module):
                pm.parent(self.data.get('zro_bind'), bind_module)
            else:
                pm.createNode('transform', p=module_bind, n=bind_module)
                pm.parent(self.data.get('zro_bind'), bind_module)
        # pre
        if pre:
            if pm.objExists(pre_module):
                pm.parent(self.data.get('zro_pre'), pre_module)
            else:
                pm.createNode('transform', p=module_pre, n=pre_module)
                pm.parent(self.data.get('zro_pre'), pre_module)

        pm.parent(module_ctrl, module_bind, module_pre, self.top_grp)

    def set_limit_z(self):
        utility.limit_z(pm.PyNode(self.data['ctrl']))

    def lock_attr(self):
        attributes.lock(self.data['ctrl'], self.attr_list)

