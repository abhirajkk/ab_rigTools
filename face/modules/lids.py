import pymel.core as pm

from lib import control

reload(control)
from utils import utility

reload(utility)

from lib import curve
reload(curve)

from lib import network
reload(network)


class LID:
    def __init__(self, side):
        self.side = side
        self.version = '0.1'
        self.origin = '{}_{}'.format(self.side, 'lidOrigin_loc')
        self.lid = ['upLid_1_loc', 'upLid_2_loc', 'upLid_3_loc',
                    'loLid_1_loc', 'loLid_2_loc', 'loLid_3_loc',
                    'lidIn_loc', 'lidOut_loc']
        self.upLid_surf = '{}_{}'.format(self.side, 'uplid_surfShape')
        self.loLid_surf = '{}_{}'.format(self.side, 'lolid_surfShape')

        self.data = {}
        self.build_surface()

    def build_surface(self):

        up_crv = curve.build_crv_from_obj([self.side + '_' + x for x in ['lidIn_loc', 'upLid_1_loc', 'upLid_2_loc',
                                                                         'upLid_3_loc', 'lidOut_loc']], degree=2)
        up_srf_name = '{}_{}'.format(self.side, 'uplid_surf')
        curve.build_surface_from_curve(up_crv, up_srf_name)

        lo_crv = curve.build_crv_from_obj([self.side + '_' + x for x in ['lidIn_loc', 'loLid_1_loc', 'loLid_2_loc',
                                                                         'loLid_3_loc', 'lidOut_loc']], degree=2)
        lo_srf_name = '{}_{}'.format(self.side, 'lolid_surf')

        curve.build_surface_from_curve(lo_crv, lo_srf_name)
        pm.delete(up_crv, lo_crv)

        grp = pm.createNode('transform', n=self.side+'_lidSurf_grp')
        pm.parent(up_srf_name, lo_srf_name, grp)

    def build(self):
        self.drive_aim_setup()
        self.add_control()
        self.add_driver_aim()

        up_surf = pm.PyNode(self.upLid_surf)
        self.aim_setup_on_surface(self.side+'_uplid', up_surf)

        lo_surf = pm.PyNode(self.loLid_surf)
        self.aim_setup_on_surface(self.side + '_lolid', lo_surf)

        self.add_main_lid_ctrl()

        self.skin_lids_surface()

        self.build_blink()

        self.build_blink_height()
        self.sub_control_visibility()
        self.setup_network()
        it_grp = LID.__name__.lower()+'_sys'
        if not pm.objExists(it_grp):
            it_grp = pm.createNode('transform', n=LID.__name__.lower()+'_sys')
        pm.parent(self.side + '_lidSurf_grp', self.side+'_lid_nurbs_bind_grp', it_grp)

    def add_driver_aim(self):

        for each in self.lid:
            item = '{}_{}'.format(self.side, each.replace('_loc', '_ctrl'))
            ctl = self.data.get(item).get_node('ctrl')
            aim_jnt = self.data['{}_{}_{}'.format(self.side, each, 'aim')]

            pm.aimConstraint(ctl, aim_jnt, aimVector=[1, 0, 0], upVector=[0, 1, 0], worldUpType='objectrotation',
                             worldUpVector=[0, 1, 0], worldUpObject=ctl)

    def add_control(self):
        for each in self.lid:
            item = '{}_{}'.format(self.side, each)
            item_node = pm.PyNode(item)
            item_name = item.replace('_loc', '_ctrl')

            ctrl_obj = control.Control(LID.__name__, self.version, self.side, self.side + '_' + LID.__name__)
            # ctrl_obj.attr_list = ['sx', 'sy', 'sz', 'v']
            ctrl_obj.build(item_node)
            self.data[item_name] = ctrl_obj

    def aim_setup_on_surface(self, vert_set, surf):
        vert_set = pm.sets(vert_set, q=1)
        vtx = pm.ls(vert_set, fl=1)

        shape = pm.PyNode(surf)
        base_name = shape.name().replace('_surfShape', '')
        cpos = pm.createNode('closestPointOnSurface')
        shape.worldSpace[0] >> cpos.inputSurface

        master_sub_grp = pm.createNode('transform', n=base_name + '_sub_grp')
        lid_bind_grp = pm.createNode('transform', n=base_name + '_sub_bind_grp')

        master_aim_tgt = pm.createNode('transform', n=base_name + '_sub_aim_grp')

        pm.parent(master_sub_grp, self.side+'_'+LID.__name__.lower()+'_ctrls')
        pm.parent(lid_bind_grp, self.side + '_' + LID.__name__.lower() + '_binds')

        for each in vtx:

            tmp_loc_shape = pm.createNode('locator')
            tmp_loc = pm.rename(tmp_loc_shape.getParent(), '{}{}'.format(base_name, '_%d_sub_loc' % vtx.index(each)))

            # aim
            pos = pm.xform(each, q=1, t=1, ws=1)
            cpos.inPosition.set(pos)

            pos = pm.createNode('pointOnSurfaceInfo', n=tmp_loc.name().replace('_loc', '_con')+'_posi')
            shape.worldSpace[0] >> pos.inputSurface

            u = cpos.parameterU.get()
            v = cpos.parameterV.get()

            pos.parameterU.set(u)
            pos.parameterV.set(v)

            sub_ctrl_obj = control.Control(LID.__name__, self.version, self.side, self.side + '_' + LID.__name__)
            sub_ctrl_obj.build(tmp_loc)
            self.data[tmp_loc.name().replace('_loc', '_ctrl')] = sub_ctrl_obj
            sub_con = sub_ctrl_obj.get_node('con')

            # pos.position >> sub_con.translate

            pm.parent(sub_ctrl_obj.get_node('zro'), master_sub_grp)
            pm.parent(sub_ctrl_obj.get_node('zro_bind'), lid_bind_grp)

            pm.delete(tmp_loc)

            # aim jnt setup per each ver pos
            aim_jnt = pm.createNode('joint', n='{}_{}'.format(base_name, 'sub_aim_%d_jnt' % vtx.index(each)))
            pm.matchTransform(aim_jnt, self.origin, pos=True, rot=False, scale=False)
            bind_jnt = pm.createNode('joint', p=aim_jnt, n='{}_{}'.format(base_name, 'sub_%d_bind' % vtx.index(each)))

            pm.joint(aim_jnt, e=1, oj='xyz', secondaryAxisOrient='yup', ch=1, zso=1)

            aim_grp = pm.createNode('transform', n='{}_{}'.format(base_name, 'sub_%d_aim_grp' % vtx.index(each)),
                                    p=master_aim_tgt)
            pos.position >> aim_grp.translate

            pm.aimConstraint(aim_grp, aim_jnt, aimVector=[1, 0, 0], upVector=[0, 1, 0], worldUpType='objectrotation',
                             worldUpVector=[0, 1, 0], worldUpObject=aim_grp)
            pm.matchTransform(bind_jnt, aim_grp)
            pm.matchTransform(sub_con, aim_grp)
            utility.matrix_constraint(bind_jnt, sub_con)
            pm.parent(aim_jnt, master_aim_tgt)

            # handle pre matrtix connection
            pre_con = sub_ctrl_obj.get_node('con_pre')
            pm.disconnectAttr(sub_con.translate, pre_con.translate)
            pm.disconnectAttr(sub_con.rotate, pre_con.rotate)
            pm.disconnectAttr(sub_con.scale, pre_con.scale)
        pm.delete(cpos)

    def drive_aim_setup(self):

        dirve_grp = pm.createNode('transform', n='{}_{}'.format(self.side, 'lid_nurbs_bind_grp'))

        for each in self.lid:
            origin = pm.createNode('joint', n='{}_{}_{}'.format(self.side, each.replace('_loc', ''), 'aim_jnt'))
            pm.matchTransform(origin, self.origin)
            jnt = pm.createNode('joint', p=origin, n='{}_{}_{}'.format(self.side, each.replace('_loc', ''), 'drv_jnt'))
            item = '{}_{}'.format(self.side, each)
            pm.matchTransform(jnt, item, pos=True, rot=False, scale=False)
            pm.joint(origin, e=1, oj='xyz', secondaryAxisOrient='yup', ch=1, zso=1)
            jnt.setAttr('jointOrient', 0, 0, 0, type='double3')

            if each.startswith('lo'):
                pm.joint(origin, e=1, oj='xyz', secondaryAxisOrient='ydown', ch=1, zso=1)

            self.data[item + '_aim'] = origin
            self.data[item + '_drv'] = jnt

            pm.parent(origin, dirve_grp)

    def add_main_lid_ctrl(self):
        # upLid
        up_lid = '{}_{}'.format(self.side, 'upLid_loc')
        up_lid_node = pm.PyNode(up_lid)
        up_lid_name = up_lid.replace('_loc', '_ctrl')

        ctrl_obj = control.Control(LID.__name__, self.version, self.side, self.side + '_' + LID.__name__)
        ctrl_obj.build(up_lid_node)
        self.data[up_lid_name] = ctrl_obj
        uplid_ctrl = ctrl_obj.get_node('ctrl')

        # loLid
        lo_lid = '{}_{}'.format(self.side, 'loLid_loc')
        lo_lid_node = pm.PyNode(lo_lid)
        lo_lid_name = lo_lid.replace('_loc', '_ctrl')

        ctrl_obj = control.Control(LID.__name__, self.version, self.side, self.side + '_' + LID.__name__)
        ctrl_obj.build(lo_lid_node)
        self.data[lo_lid_name] = ctrl_obj
        lolid_ctrl = ctrl_obj.get_node('ctrl')

        # upLid
        for each in ['upLid_1', 'upLid_2', 'upLid_3']:
            item = '{}_{}_{}'.format(self.side, each, 'ctrl')
            item_ato = '{}_{}_{}'.format(self.side, each, 'ctrl_ato')
            #item_inst = self.data[item]
            ato_node = self.data.get(item).get_node('ato')

            con = pm.parentConstraint(uplid_ctrl, ato_node, mo=1)

            # follow main with blend 0.5
            if each != 'upLid_2':
                utility.eye_weight_constraints(con, item_ato)

        # loLid
        for each in ['loLid_1', 'loLid_2', 'loLid_3']:
            item = '{}_{}_{}'.format(self.side, each, 'ctrl')
            item_ato = '{}_{}_{}'.format(self.side, each, 'ctrl_ato')
            # item_inst = self.data[item]
            ato_node = self.data.get(item).get_node('ato')

            con = pm.parentConstraint(lolid_ctrl, ato_node, mo=1)

            # follow main with blend 0.5
            if each != 'loLid_2':
                utility.eye_weight_constraints(con, item_ato)

    def skin_lids_surface(self):
        pm.skinCluster([self.side+'_lidIn_jnt', self.side+'_upLid_1_drv_jnt', self.side+'_upLid_2_drv_jnt',
                        self.side+'_upLid_3_drv_jnt', self.side+'_lidOut_jnt'], self.upLid_surf, tsb=1)

        pm.skinCluster([self.side + '_lidIn_jnt', self.side + '_loLid_1_drv_jnt', self.side + '_loLid_2_drv_jnt',
                        self.side + '_loLid_3_drv_jnt', self.side + '_lidOut_jnt'], self.loLid_surf, tsb=1)

    def build_blink(self):
        node = pm.PyNode(self.side+'_upLid_ctrl')
        pm.addAttr(self.side+'_upLid_ctrl', ln='extra', nn='__extra__', k=1)

        pm.addAttr(self.side + '_upLid_ctrl', ln='blink', min=0, max=100, k=1)

        pm.addAttr(self.side + '_upLid_ctrl', ln='blinkHeight', min=-100, max=100, k=1)

        # uplid
        sdk = pm.createNode('setRange', n=self.side + '_upLid_blink_sr')
        node.blink >> sdk.valueY

        sdk.maxY.set(1.5)
        sdk.oldMaxY.set(100)
        sdk.outValueY >> self.side+'_upLid_ctrl_ato.ty'

        # lolid
        lo_sdk = pm.createNode('setRange', n=self.side + '_loLid_blink_sr')
        node.blink >> lo_sdk.valueY

        lo_sdk.maxY.set(0.5)
        lo_sdk.oldMaxY.set(100)
        lo_sdk.outValueY >> self.side + '_loLid_ctrl_ato.ty'

    def build_blink_height(self):
        node = pm.PyNode(self.side + '_upLid_ctrl')
        sdk_node = self.data.get(self.side + '_upLid_ctrl').get_node('drn')
        # uplid
        sdk = pm.createNode('setRange', n=self.side + '_upLid_blinkHeight_sr')
        node.blinkHeight >> sdk.valueY

        sdk.minY.set(-1.5)
        sdk.maxY.set(1.5)
        sdk.oldMinY.set(-100)
        sdk.oldMaxY.set(100)
        sdk.outValueY >> sdk_node.ty

        # lolid
        lo_sdk = pm.createNode('setRange', n=self.side + '_loLid_blinkHeight_sr')
        node.blinkHeight >> lo_sdk.valueY

        lo_sdk.minY.set(1.5)
        lo_sdk.maxY.set(-1.5)
        lo_sdk.oldMinY.set(-100)
        lo_sdk.oldMaxY.set(100)
        lo_sdk.outValueY >> sdk_node.ty

    def sub_control_visibility(self):
        node = pm.PyNode(self.side + '_upLid_ctrl')
        pm.addAttr(self.side + '_upLid_ctrl', ln='showSubCtrls', at='bool', k=1)

        pm.connectAttr(node.showSubCtrls, self.side+'_uplid_sub_grp.v')
        pm.connectAttr(node.showSubCtrls, self.side + '_lolid_sub_grp.v')

    def setup_network(self):
        for key in self.data.keys():
            if key.endswith('_ctrl'):
                net = network.Network(LID.__name__)
                net.add_attr(key)
                net.set_connection(pm.PyNode(key), key)

    def get_sub_bind(self):
        sub_binds = []
        for key in self.data.keys():
            if key.endswith('_sub_ctrl'):
                inst = self.data.get(key)
                sub_binds.append(inst.get_node('bind'))
        return sub_binds

