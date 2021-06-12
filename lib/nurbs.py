import pymel.core as pm


def obj_on_surface(vert_set, surf, rotation=False, child=False, joint=False):
    vert_set = pm.sets(vert_set, q=1)
    vtx = pm.ls(vert_set, fl=1)

    shape = pm.PyNode(surf)
    cpos = pm.createNode('closestPointOnSurface')
    shape.worldSpace[0] >> cpos.inputSurface

    master_aim_grp = pm.createNode('transform', n=shape.name()+'_driver_grps')

    for each in vtx:
        # aim
        pos = pm.xform(each, q=1, t=1, ws=1)
        cpos.inPosition.set(pos)

        pos = pm.createNode('pointOnSurfaceInfo')
        shape.worldSpace[0] >> pos.inputSurface

        u = cpos.parameterU.get()
        v = cpos.parameterV.get()

        pos.parameterU.set(u)
        pos.parameterV.set(v)

        grp = pm.createNode('transform', n='{}_{}'.format(shape.name(), 'sub_%d_grp' % vtx.index(each)),
                            p=master_aim_grp)

        if child:
            pm.createNode('transform', n='{}_{}'.format(shape.name(), 'sub_%d_ctrl' % vtx.index(each)),
                                       p=grp)
        if joint:
            if pm.objExists('{}_{}'.format(shape.name(), 'sub_%d_ctrl' % vtx.index(each))):
                pm.createNode('joint', n='{}_{}'.format(shape.name(), 'sub_%d_bind' % vtx.index(each)),
                              p='{}_{}'.format(shape.name(), 'sub_%d_ctrl' % vtx.index(each)))
            else:
                pm.createNode('joint', n='{}_{}'.format(shape.name(), 'sub_%d_bind' % vtx.index(each)), p=grp)

        pos.position >> grp.translate

        if rotation:
            aim = pm.createNode('aimConstraint')
            pos.normal >> aim.target[0].targetTranslate
            pos.tangentV >> aim.worldUpVector

            aim.constraintRotate >> grp.rotate
    return master_aim_grp


def get_equal_points_on_surface(crv, count, u=True, v=False):
    u_max = crv.minMaxRangeU.get()[-1]

    v_max = crv.minMaxRangeV.get()[-1]

    cpos = pm.createNode('pointOnSurfaceInfo')
    crv.worldSpace[0] >> cpos.inputSurface
    position = []
    if u:
        for i in range(count):
            u_value = i*u_max/(count-1.0)
            cpos.paramterU.set(u_value)
            cpos.paramterV.set(0.5)
            position.append(cpos.position.get())
    if v:
        for i in range(count):
            v_value = i*v_max/(count-1.0)
            cpos.paramterU.set(0.5)
            cpos.paramterV.set(v_value)
            position.append(cpos.position.get())
    pm.delete(cpos)
    return position


def get_vert_positons_on_surf(vert_set, surf):
    positions = []
    vert_set = pm.sets(vert_set, q=1)
    vtx = pm.ls(vert_set, fl=1)

    shape = pm.PyNode(surf)
    cpos = pm.createNode('closestPointOnSurface')
    shape.worldSpace[0] >> cpos.inputSurface

    for each in vtx:
        # aim
        pos = pm.xform(each, q=1, t=1, ws=1)
        cpos.inPosition.set(pos)

        pos = pm.createNode('pointOnSurfaceInfo')
        shape.worldSpace[0] >> pos.inputSurface

        u = cpos.parameterU.get()
        v = cpos.parameterV.get()

        pos.parameterU.set(u)
        pos.parameterV.set(v)

        positions.append(pos.position.get())
        pm.delete(pos)
    pm.delete(cpos)
    return positions


def attach_obj_to_surface(obj, surf, rot=False):
    value = pm.xform(obj, q=1, t=1, ws=1)

    shape = pm.PyNode(surf)
    cpos = pm.createNode('closestPointOnSurface')
    shape.worldSpace[0] >> cpos.inputSurface
    cpos.inPosition.set(value)

    pos = pm.createNode('pointOnSurfaceInfo', n=obj.name()+'_posi')
    shape.worldSpace[0] >> pos.inputSurface

    u = cpos.parameterU.get()
    v = cpos.parameterV.get()

    pos.parameterU.set(u)
    pos.parameterV.set(v)

    pos.position >> obj.translate
    if rot:
        print "do it later"
    pm.delete(cpos)
