import pymel.core as pm
import json
import os
import maya.api.OpenMaya as om


def getDagPath(node):
    sel = om.MSelectionList()
    sel.add(node)
    d = om.MDagPath()
    sel.getDagPath(0, d)
    return d


def average_transforms(source_a, source_b, target,  att='translate'):
    pma = pm.createNode('plusMinusAverage')
    pma.operation.set(3)
    if att == 'translate':
        source_a.translate >> pma.input3D[0]
        source_b.translate >> pma.input3D[1]

        pma.output3D >> target.translate
    elif att == 'rotate':
        source_a.rotate >> pma.input3D[0]
        source_b.rotate >> pma.input3D[1]

        pma.output3D >> target.rotate


def get_shape_color():
    for each in pm.ls(sl=1):
        shape = each.getShape()
        return shape.overrideColor.get()


def set_shape_color(color=6):
    for each in pm.ls(sl=1):
        shape = each.getShape()
        shape.overrideEnabled.set(True)
        shape.overrideColor.set(color)


def build_obj_at_positions(positions, node='locator'):
    for each in positions:
        obj = pm.createNode(node)
        obj.parent(0).translate.set(each)


def weighted_pair_blend(input_a, input_b, target, w=0.5):
    blend = pm.createNode('pairBlend')
    blend.weight.set(w)

    input_a.translate >> blend.inTranslate1
    input_b.translate >> blend.inTranslate2

    input_a.rotate >> blend.inRotate1
    input_b.rotate >> blend.inRotate2

    blend.outTranslate >> target.translate
    blend.outRotate >> target.rotate


def eye_weight_constraints(source, target, w=0.5, attr=False):
    source = pm.PyNode(source)
    target = pm.PyNode(target)

    blend = pm.createNode('pairBlend', n=target.name()+'_pb')
    blend.weight.set(w)

    source.constraintTranslate >> blend.inTranslate1
    source.constraintRotate >> blend.inRotate1

    # disconnect first
    pm.disconnectAttr(source.constraintTranslate.constraintTranslateX, target.translateX)
    pm.disconnectAttr(source.constraintTranslate.constraintTranslateY, target.translateY)
    pm.disconnectAttr(source.constraintTranslate.constraintTranslateZ, target.translateZ)

    pm.disconnectAttr(source.constraintRotate.constraintRotateX, target.rotateX)
    pm.disconnectAttr(source.constraintRotate.constraintRotateY, target.rotateY)
    pm.disconnectAttr(source.constraintRotate.constraintRotateZ, target.rotateZ)

    blend.outTranslate >> target.translate
    blend.outRotate >> target.rotate

    if attr:
        pm.addAttr(target, ln='follow', max=1, min=0, dv=0.5, k=1)
        pm.connectAttr(target.follow, blend.weight)
    return blend


def mirror_selected_obj(translation=True, rotation=False):
    for each in pm.ls(sl=1):
        if each.name().startswith('L_'):
            target = pm.PyNode(each.name().replace('L_', 'R_'))
        elif each.name().startswith('R_'):
            target = pm.PyNode(each.name().replace('L_', 'R_'))
        else:
            return
        current = each.translate.get()

        if translation:
            target.translate.set(current[0]*-1, current[1], current[2])
        if rotation:
            print ("work later")


def limit_z(obj):
    node = pm.PyNode(obj)
    pm.addAttr(obj, ln='Z', k=True)
    mdl = pm.createNode('multDoubleLinear', n=node.name()+'_Z_mdl')
    mdl.input2.set(0.1)
    node.Z >> mdl.input1
    mdl.output >> obj.tz

    node.tz.setLocked(True)
    node.tz.setKeyable(False)


def export_proxy_loc(file_name):
    sel = pm.ls(sl=1)
    if not sel:
        return
    data = {}
    for each in sel:
        data[each.name()] = pm.xform(each, q=1, t=1, ws=1)

    # save
    path = pm.system.sceneName().dirname()
    file_name = os.path.join(path, '{}.{}'.format(file_name, 'json'))
    with open(file_name, 'w') as data_handle:
        json.dump(data, data_handle)

    print ("export done !!!")


def rebuild_proxy_loc_from_file(file_name):
    path = pm.system.sceneName().dirname()
    file_name = os.path.join(path, '{}.{}'.format(file_name, 'json'))

    if os.path.exists(file_name):
        with open(file_name) as json_file:
            data = json.load(json_file)

            for each in data.keys():
                node = pm.createNode('locator', n=each+'Shape')
                pm.rename(node.getParent(), each)
                node.getParent().translate.set(data[each])


def matrix_constraint(src, tgt):

    parentWorldMatrix = getDagPath(src.name()).inclusiveMatrix()
    childWorldMatrix = getDagPath(tgt.name()).inclusiveMatrix()
    offset = childWorldMatrix * parentWorldMatrix.inverse()
    pm.addAttr(src, ln='offset', attributeType='matrix')
    pm.setAttr('{}.offset'.format(src), [offset(i, j) for i in range(4) for j in range(4)],
               type='matrix')

    decmpose = pm.createNode('decomposeMatrix', n=tgt.name()+'_dm')
    mult_matrix = pm.createNode('multMatrix', n=tgt.name()+'_mm')
    pm.connectAttr('{}.offset'.format(src), '{}.matrixIn[0]'.format(mult_matrix))
    # pm.setAttr('{}.matrixIn[0]'.format(mult_matrix), offset, type='matrix')
    pm.connectAttr('{}.worldMatrix'.format(src), '{}.matrixIn[1]'.format(mult_matrix))
    pm.connectAttr('{}.matrixSum'.format(mult_matrix), '{}.inputMatrix'.format(decmpose))

    pm.connectAttr(decmpose.outputTranslate, tgt.translate)
    pm.connectAttr(decmpose.outputRotate, tgt.rotate)


# remove not in use
def get_network(part):
    nodes = []
    for node in pm.ls(type='network'):
        if node.attr('part').get() == part:
            nodes.append(node)

    if nodes:
        return nodes
    else:
        return None


def get_template_from_tag(part_module):
    nodes = []
    for node in pm.ls(type='renderBox'):
        node_t = node.getParent()
        if node_t.attr('module').get() == part_module:
            nodes.append(node_t)
    if nodes:
        return nodes
    else:
        return None


def get_transform_from_tag(part):
    nodes = []
    for node in pm.ls(type='transform'):
        if node.attr('part').get() == part:
            nodes.append(node)
    if nodes:
        return nodes
    else:
        return None

