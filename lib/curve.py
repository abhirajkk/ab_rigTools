import json
import os

import pymel.core as pm


def build_crv_from_obj(objs, degree=3, space='world'):
    positions = []
    for each in objs:
        if space == 'world':
            positions.append(pm.xform(each, q=1, ws=1, t=1))
        elif space == 'object':
            positions.append(pm.xform(each, q=1, os=1, t=1))
        else:
            return
    crv = build_crv_from_pos(positions, degree)
    return crv


def build_crv_from_pos(positions, degree=3):
    return pm.curve(d=degree, p=positions)


def get_equal_points_on_curve(crv, count):
    u_max = crv.minMaxValue.get()[-1]

    cpos = pm.createNode('pointOnCurveInfo')
    crv.worldSpace[0] >> cpos.inputCurve
    u_position = []
    for i in range(count):
        value = i*u_max/(count-1.0)
        cpos.parameter.set(value)
        pos = cpos.position.get()
        u_position.append(pos)
    pm.delete(cpos)
    return u_position


def get_closest_points_on_curve():
    for each in pm.ls(sl=1):
        # need to check the type of selection
        pos = pm.xform(each, q=1, t=1, ws=1)


def build_surface_from_curve(crv, name, distance=0.05):
    crv_1 = pm.offsetCurve(crv, ch=True, rn=False, cb=2, st=True, cl=True,
                           cr=0, d=distance, tol=0.01, sd=5, ugn=False)
    crv_2 = pm.offsetCurve(crv, ch=True, rn=False, cb=2, st=True, cl=True,
                           cr=0, d=distance*-1, tol=0.01, sd=5, ugn=False)

    srf = pm.loft(crv_1, crv_2, ch=True, u=True, c=False, ar=1, d=3, ss=1, rn=0, po=0, rsn=True)

    pm.rebuildSurface(srf, ch=1, rpo=1, rt=0, end=1, kr=0, kcp=0, kc=0, su=3, du=2, sv=1, dv=3,
                      tol=0.01, fr=0, dir=2)
    pm.rename(srf[0], name)
    pm.delete(crv_1, crv_2)


def mirror_shapes():
    for each in pm.ls(sl=1):
        shape = each.getShape()
        pos = shape.getCVs(space='world')
        new_pos = []
        if each.name().startswith('L_'):
            node = each.name().replace('L_', 'R_')

        elif each.name().startswith('R_'):
            node = each.name().replace('R_', 'L_')

        else:
            print ("cant find L or R in selection")
            return

        if pm.objExists(node):
            for pnt in pos:
                new_pos.append(pm.datatypes.Point(pnt[0] * -1, pnt[1], pnt[2]))
        else:
            print ("node dose not exist")
            return
        target_node = pm.PyNode(node)
        target_shape = target_node.getShape()
        target_shape.setCVs(new_pos, space='world')
        target_shape.updateCurve()


def mirror_color():
    for each in pm.ls(sl=1):
        color = get_shape_color(each)
        if each.name().startswith('L_'):
            node = each.name().replace('L_', 'R_')

        elif each.name().startswith('R_'):
            node = each.name().replace('R_', 'L_')
        else:
            return
        if not pm.objExists(node):
            return
        set_shape_color(node, color)


def get_shape_color(crv):
    crv = pm.PyNode(crv)
    shape = crv.getShape()
    # return shape.overrideColor.get()
    return crv.overrideColor.get()


def set_shape_color(crv, color=6):
    node = pm.PyNode(crv)
    shape = node.getShape()
    shape.overrideEnabled.set(True)
    shape.overrideColor.set(color)


def export_shape_data(curve_objs, file_name, path=None):
    shape_data = {}
    if path:
        path = path
    else:
        path = pm.system.sceneName().dirname()
    for each in curve_objs:
        node = pm.PyNode(each)
        shape = node.getShape()
        positions = shape.getCVs(space='world')
        pos = []
        for item in positions:
            pos.append([item[0], item[1], item[2]])

        color = get_shape_color(each)

        shape_data[shape.name()] = {'pos': pos,
                                    'color': color}

    # save
    file_name = os.path.join(path, '{}.{}'.format(file_name, 'json'))
    with open(file_name, 'w') as data_handle:
        json.dump(shape_data, data_handle)

    print ("curves shape export done !!!")


def import_shape_data(file_name, path=None):
    if path:
        path = path
    else:
        path = pm.system.sceneName().dirname()

    file_name = os.path.join(path, '{}.{}'.format(file_name, 'json'))

    if os.path.exists(file_name):
        with open(file_name) as json_file:
            data = json.load(json_file)

        for key in data.keys():
            pos = data[key]['pos']
            dt_pos = []
            all_pos = []
            for pnt in pos:
                dt_pos.append(pm.datatypes.Point(pnt[0], pnt[1], pnt[2]))
                all_pos.append((pnt[0], pnt[1], pnt[2]))
            if pm.objExists(key):
                node = pm.PyNode(key)
            else:
                node = build_crv_from_pos(all_pos, degree=3)
                pm.rename(node, key.replace('Shape', ''))

            node.setCVs(dt_pos, space='world')
            node.updateCurve()
            #set_shape_color(node.getParent(), data[key]['color'])
            set_shape_color(node, data[key]['color'])
        print ("curves import done ::!")
    else:
        print ("The file not found!! please check.:)")
        return


def build_curve_from_edge():
    """# sel = pm.ls(sl=1, fl=1)
    edge_to_vtx = pm.polyListComponentConversion(tv=True, bo=True)
    vtxs = pm.ls(edge_to_vtx, fl=1)

    positions = []
    for each in vtxs:
        pos = pm.xform(each, q=1, t=1, ws=1)
        positions.append(pos)
    crv = build_crv_from_pos(positions)"""
    crv = pm.polyToCurve(form=2, degree=3, ch=0)[0]
    new_crv = rebuild_curve(crv)
    return new_crv


def build_vtx_set_from_edge(name):
        vtx = pm.ls(pm.polyListComponentConversion(tv=1, bo=1), fl=1)
        print (vtx)
        pm.sets(vtx, n=name)


def rebuild_curve(crv, degree=3, cvs=None):
    crv_tfm = pm.PyNode(crv)
    crv = crv_tfm.getShape()
    if cvs:
        return pm.rebuildCurve(crv_tfm, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=cvs, d=degree, tol=0.01)
    else:
        return pm.rebuildCurve(crv_tfm, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=crv.numCVs(), d=degree, tol=0.01)


def place_objs_on_curve(curve, objs):
    crv = pm.PyNode(curve)
    pos = get_equal_points_on_curve(crv, len(objs))
    for i, obj in enumerate(objs):
        node = pm.PyNode(obj)
        node.translate.set(pos[i])


def place_obj_on_parameter(curve, obj, parameter):
    crv = pm.PyNode(curve)
    shape = crv.getShape()
    pnt = shape.getPointAtParam(parameter)
    obj_node = pm.PyNode(obj)
    obj_node.translate.set(pnt)


def attach_objs_on_curve(curve, objs):
    crv = pm.PyNode(curve)
    count = len(objs)
    for i in range(count):
        parm = i*1.0/(count-1.0)
        poci = pm.createNode('pointOnCurveInfo')
        crv.worldSpace[0] >> poci.inputCurve
        poci.parameter.set(parm)
        poci.position >> objs[i].translate


def attach_obj_on_parameter(curve, obj, parameter):
    crv = pm.PyNode(curve)
    poci = pm.createNode('pointOnCurveInfo')
    crv.worldSpace[0] >> poci.inputCurve
    poci.parameter.set(parameter)
    poci.position >> obj.translate
