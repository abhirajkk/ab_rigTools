import pymel.core as pm
import maya.api.OpenMaya as om 


def get_dagpath(obj):
    mSel = om.MSelectionList()
    mSel.add(obj)
    mDag=mSel.getDagPath(0)
    return mDag


def get_dependNode(obj):
    mSel = om.MSelectionList()
    mSel.add(obj)
    mDep=mSel.getDependNode(0)
    return mDep


def get_matrix_from_node(obj):
    node = get_dependNode(obj)

    mDfnDep = om.MFnDependencyNode(node)
    plug = mDfnDep.findPlug("worldInverseMatrix",0)
    mPlug_mobj = plug.elementByLogicalIndex(0).asMObject()
    mat = om.MFnMatrixData(mPlug_mobj).matrix()
    return mat


def get_points_from_curve(crv, pointAt = [0.0, 0.5, 0.75, 1.0]):
    crv_dag = get_dagpath(crv)

    mFn_curve = om.MFnNurbsCurve(crv_dag)
    points_on_curve = []
    for pnts in pointAt:
        point = mFn_curve.getPointAtParam(pnts,om.MSpace.kWorld)
        points_on_curve.append(point)
    return points_on_curve


def set_driven_key(driver_obj, driver_attr, driven_obj, driven_atrr, **kwargs):

    pm.setDrivenKeyframe("{}.{}".format(driven_obj, driven_atrr), cd="{}.{}".format(driver_obj, driver_attr), **kwargs)


def set_drivenKey_from_curve(crv, driver_obj, driver_attr, driven_obj, driven_attr):

    # set key on default zeoo
    set_driven_key(driver_obj, driver_attr, driven_obj, driven_attr, itt="spline", ott="spline")

    driver_ob_wim = get_matrix_from_node(driver_obj)
    crv_pnt_pos = get_points_from_curve(crv)

    # set key on curve points
    for pnt in crv_pnt_pos:
        driver_pos = pnt*driver_ob_wim
        if driver_attr == 'ty':
            axis = driver_pos.y
        elif driver_attr == 'tx':
            axis = driver_pos.x
        else:
            axis = driver_pos.y

        pm.setAttr("{}.{}".format(driver_obj, driver_attr), axis)
        pm.setAttr("{}.{}".format(driven_obj, driven_attr), driver_pos.z)
        set_driven_key(driver_obj, driver_attr, driven_obj, driven_attr, itt="spline", ott="spline")
        pm.setAttr("{}.{}".format(driver_obj, driver_attr), 0)

# set_drivenKey_from_curve('curveShape1', "ctrl1", "ty", "sdk1", "tz")
