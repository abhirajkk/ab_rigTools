import pymel.core as pm

from importlib import reload
from lib import attributes
reload(attributes)


class Template:
    def __init__(self):
        self.part_grp = None
        if pm.objExists('template_grp'):
            self.template_grp = 'template_grp'
        else:
            self.template_grp = pm.createNode('transform', n='template_grp')

    def build(self, part, name, position, rotation):

        if pm.objExists(part+'_grp'):
            self.part_grp = part+'_grp'
        else:
            self.part_grp = pm.createNode('transform', n= part+'_grp')

        box = self.rendbox(name, position[0], position[1], position[2], rotation[0], rotation[1], rotation[2],
                           self.part_grp)

        pm.parent(self.part_grp, self.template_grp)

        # component, modules, version, side, part
        attributes.add_tag(box, 'FACE', self.__class__.__name__,
                           "0.1", name.split('_')[0],
                           '{}_{}'.format(name.split('_')[0], part))

    def set_template_pos(self, obj, pos):

        '''for i, each in enumerate(obj):
            node = self.network.get_connection(each)
            node.translate.set(pos[i])'''
        pass

    @staticmethod
    def rendbox(name, tx, ty, tz, rx, ry, rz, parentObj=None):
        skBoxShape = pm.createNode('renderBox')
        pm.setAttr((skBoxShape + '.size'), 0.05, 0.05, 0.05)
        skBox = pm.listRelatives(skBoxShape, parent=True)
        pm.setAttr((skBox[0] + '.displayRotatePivot'), 1)
        pm.setAttr((skBox[0] + '.translate'), tx, ty, tz)
        pm.setAttr((skBox[0] + '.rotate'), rx, ry, rz)
        skBoxFnlName = pm.rename(skBox[0], name)
        try:
            if parentObj:
                pm.parent(skBoxFnlName, parentObj)
        except TypeError:
            pass
        return skBoxFnlName

    @staticmethod
    def build_crv_from_obj(objs, degree=1, space='world'):
        positions = []
        for each in objs:
            if space == 'world':
                positions.append(pm.xform(each, q=1, ws=1, t=1))
            elif space == 'object':
                positions.append(pm.xform(each, q=1, os=1, t=1))
            else:
                return
        crv = Template.build_crv_from_pos(positions, degree)
        crv_shape = crv.getShape()
        for i, each in enumerate(objs):
            mat = pm.createNode('decomposeMatrix')
            pm.connectAttr(each + '.worldMatrix[0]', mat.inputMatrix)
            pm.connectAttr(mat.outputTranslate, crv_shape + '.controlPoints[%d]' % i)
        pm.parent(crv, 'template_grp')
        crv.overrideEnabled.set(1)
        crv.overrideDisplayType.set(1)
        return crv

    @staticmethod
    def build_crv_from_pos(positions, degree=1):
        return pm.curve(d=degree, p=positions)
