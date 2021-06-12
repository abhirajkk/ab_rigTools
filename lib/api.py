import maya.api.OpenMaya as om


def get_dagPath(object):
    mSel = om.MSelectionList()
    mSel.add(object)
    mObj = mSel.getDagPath(0)
    return mObj


def get_dependNode(object):
    mSel = om.MSelectionList()
    mSel.add(object)
    mDep = mSel.getDependNode(0)
    return mDep


def nurbs_mfn(object):
    mDep = get_dependNode(object)
    mfn = om.MFnNurbsSurface(mDep)
    return mfn