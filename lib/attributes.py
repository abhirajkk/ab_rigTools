import maya.api.OpenMaya as om
import pymel.core as pm


def add_tag(obj, component, modules, version, side, part):
    sel = om.MSelectionList()
    sel.add(obj.name())
    mob = sel.getDependNode(0)

    fn_cAttr = om.MFnCompoundAttribute()
    fn_tAttr = om.MFnTypedAttribute()

    c_attr = fn_cAttr.create('RIG', 'RIG')

    face_attr = fn_tAttr.create('component', 'component', om.MFnNumericData.kString)

    module_attr = fn_tAttr.create('module', 'module', om.MFnNumericData.kString)
    ver_attr = fn_tAttr.create('version', 'version', om.MFnNumericData.kString)
    side_attr = fn_tAttr.create('side', 'side', om.MFnNumericData.kString)
    part_attr = fn_tAttr.create('part', 'part', om.MFnNumericData.kString)

    fn_cAttr.addChild(face_attr)
    fn_cAttr.addChild(module_attr)
    fn_cAttr.addChild(ver_attr)
    fn_cAttr.addChild(side_attr)
    fn_cAttr.addChild(part_attr)

    fn_dep = om.MFnDependencyNode(mob)
    fn_dep.addAttribute(c_attr)

    face = fn_dep.findPlug('component', True)
    face.setString(component)

    mod = fn_dep.findPlug('module', True)
    mod.setString(modules)

    mod = fn_dep.findPlug('version', True)
    mod.setString(version)

    mod = fn_dep.findPlug('side', True)
    mod.setString(side)

    mod = fn_dep.findPlug('part', True)
    mod.setString(part)


def lock(obj, attributes=['v']):
    for attr in attributes:
        pm.setAttr('{}.{}'.format(obj, attr), lock=True, k=False)


def un_lock(obj, attributes=['v']):
    for attr in attributes:
        pm.setAttr('{}.{}'.format(obj, attr), lock=False, k=True)


def reset(obj):
    rest = {'tx': 0.0, 'ty': 0.0, 'tz': 0.0, 'rx': 0.0, 'ry': 0.0, 'rz': 0.0, 'sx': 1.0, 'sy': 1.0, 'sz': 1.0}
    obj = pm.PyNode(obj)
    for att in rest.keys():
        try:
            obj.attr(att).set(rest[att])
        except:
            print ('{}.{} has been loacked !!'.format(obj.name(), att))
