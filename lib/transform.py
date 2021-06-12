import math
import pymel.core as pm


def mirror_selected(plane='XY', side='L>R', rotate=True):
    sel = pm.ls(sl=1)
    for each in sel:
        if side == 'L>R':
            obj = each.name().replace('L_', 'R_')

        elif side == 'R>L':
            obj = pm.PyNode(each.replace('L_', 'R_'))
        else:
            obj = each

        if pm.objExists(obj):
            node = pm.PyNode(obj)
        else:
            node = pm.duplicate(each, n=obj)[0]

        # X Y Plane
        if plane == 'XY':
            mirror_axis = [-1, 0, 0, 0,
                           0, 1, 0, 0,
                           0, 0, 1, 0,
                           0, 0, 0, 0]
        elif plane == 'YX':
            mirror_axis = [1, 0, 0, 0,
                           0, -1, 0, 0,
                           0, 0, 1, 0,
                           0, 0, 0, 0]
        elif plane == 'ZX':
            mirror_axis = [1, 0, 0, 0,
                           0, 1, 0, 0,
                           0, 0, -1, 0,
                           0, 0, 0, 0]

        mirror_mat = pm.datatypes.Matrix(mirror_axis)
        current_mat = pm.datatypes.Matrix(each.worldMatrix.get())
        mirror = current_mat * mirror_mat
        result = pm.datatypes.TransformationMatrix(mirror)

        trans = result.getTranslation(space='world')
        node.translate.set(trans)

        if rotate:
            rot = result.getRotation()
            node.rotate.set(math.degrees(rot.x), math.degrees(rot.y), math.degrees(rot.z))


def mirror_with_neg_scale(plane='XY', side='L>R'):
    sel = pm.ls(sl=1)

    for each in sel:
        if side == 'L>R':
            obj = each.name().replace('L_', 'R_')

        elif side == 'R>L':
            obj = pm.PyNode(each.replace('L_', 'R_'))
        else:
            obj = each

        if pm.objExists(obj):
            node = pm.PyNode(obj)
        else:
            node = pm.duplicate(each, n=obj)[0]

        tmp_neg_node = pm.createNode('transform')
        pm.parent(node, tmp_neg_node)

        if plane == 'XY':
            tmp_neg_node.scale.set(-1, 1, 1)

        elif plane == 'YX':
            tmp_neg_node.scale.set(1, 1, -1)

        pm.makeIdentity(tmp_neg_node, s=True, a=True)
        pm.parent(node, world=True)
        pm.delete(tmp_neg_node)


def average(src, tgt, connect=True):
    pma = pm.createNode('plusMinusAverage', n=tgt.name()+'_pma')
    pma.operation.set(3)
    for i, each in enumerate(src):
        # each.translate >> pma.input3D['%d']%i
        pm.connectAttr('{}.{}'.format(each, 'translate'), '%s.input3D[%d]' % (pma, i))
        if connect:
            pma.output3D >> tgt.translate


def parent_constraint_with_matrix():
    pass
    '''for each in ctls:
        rivet_node = pm.PyNode(each.name().replace('_ctrl', '_rivet'))

        riv_node = pm.PyNode(each.name().replace('_ctrl', '_riv'))

        con_node = pm.PyNode(each.name().replace('_ctrl', '_con'))

        piv_node = pm.PyNode(each.name().replace('_ctrl', '_piv'))

        offset = pm.createNode('multMatrix')

        con_node.worldMatrix[0] >> offset.matrixIn[0]

        get_wm = pm.getAttr(rivet_node.worldInverseMatrix[0])

        pm.setAttr(offset.matrixIn[1], get_wm)

        mult = pm.createNode('multMatrix')
        offset.matrixSum >> mult.matrixIn[0]
        rivet_node.worldMatrix[0] >> mult.matrixIn[1]
        piv_node.parentInverseMatrix[0] >> mult.matrixIn[2]

        dcom = pm.createNode('decomposeMatrix')
        mult.matrixSum >> dcom.inputMatrix

        dcom.outputTranslate >> riv_node.translate
        dcom.outputRotate >> riv_node.rotate'''
