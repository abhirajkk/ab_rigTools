
import pymel.core as pm

from lib import control

reload(control)
from utils import utility

reload(utility)
from lib import nurbs
reload(nurbs)
from lib import curve

from lib import network
reload(network)


class EYERING:
    def __init__(self, side):
        self.side = side
        self.version = '0.1'
        # self.origin = '{}_{}'.format(self.side, 'lidOrigin')

        self.upLid_surf = '{}_{}'.format(self.side, 'upRing_Surf')
        self.loLid_surf = '{}_{}'.format(self.side, 'loRing_Surf')

        self.data = {}
        self.up_bind_jnts = []
        self.lo_bind_jnts = []
        self.build_surface()

    def build_surface(self):
        up_crv = curve.build_crv_from_obj([self.side + '_' + x for x in ['ringIn_loc', 'upRing_1_loc', 'upRing_2_loc',
                                                                         'upRing_3_loc', 'ringOut_loc']], degree=2)
        up_srf_name = '{}_{}'.format(self.side, 'upRing_Surf')
        curve.build_surface_from_curve(up_crv, up_srf_name)

        lo_crv = curve.build_crv_from_obj([self.side + '_' + x for x in ['ringIn_loc', 'loRing_1_loc', 'loRing_2_loc',
                                                                         'loRing_3_loc', 'ringOut_loc']], degree=2)
        lo_srf_name = '{}_{}'.format(self.side, 'loRing_Surf')

        curve.build_surface_from_curve(lo_crv, lo_srf_name)
        pm.delete(up_crv, lo_crv)

        grp = pm.createNode('transform', n=self.side + '_ring_surf_grp')
        pm.parent(up_srf_name, lo_srf_name, grp)

    def build(self):
        self.build_major()
        self.build_up_ring()
        self.build_lo_ring()
        self.build_corners()
        self.build_follow()

        self.setup_network()

        it_grp = EYERING.__name__.lower() + '_sys'
        if not pm.objExists(it_grp):
            it_grp = pm.createNode('transform', n=EYERING.__name__.lower() + '_sys')
        pm.parent(self.side + '_ring_surf_grp', it_grp)

    def build_up_ring(self):
        uplid = ['upRing_1_loc', 'upRing_2_loc', 'upRing_3_loc']

        for each in uplid:
            item = '{}_{}'.format(self.side, each)
            ctrl_name = item.replace('_loc', '_ctrl')
            item_node = pm.PyNode(item)
            ctrl_obj = control.Control(EYERING.__name__, self.version, self.side, self.side + '_' + EYERING.__name__)
            ctrl_obj.build(item_node)
            self.data[ctrl_name] = ctrl_obj

            # ctrl bind jnt
            self.up_bind_jnts.append(ctrl_obj.get_node('bind'))

            # build connection to major
            up_major = self.data[self.side + '_upRing_ctrl'].get_node('ctrl')
            sub_ctrl_ato = ctrl_obj.get_node('ato')

            con = pm.parentConstraint(up_major, sub_ctrl_ato, mo=1)
            if item == self.side+'_upRing_2_loc':
                utility.eye_weight_constraints(con, sub_ctrl_ato, w=0)
            else:
                utility.eye_weight_constraints(con, sub_ctrl_ato, w=0.25)

        # build main bind joints on surface
        # bind_jnts = nurbs.obj_on_surface(self.side + '_upring', self.upLid_surf, rotation=False, joint=True)
        # pm.parent(bind_jnts, self.side+'_eyering_binds')
        pnts_on_surface = nurbs.get_vert_positons_on_surf(self.side + '_upring', self.upLid_surf)
        for i, pnt in enumerate(pnts_on_surface):
            tmp_loc_shape = pm.createNode('locator')
            tmp_loc = pm.rename(tmp_loc_shape.getParent(), self.side+'_upRing%d_sub_loc' % i)
            tmp_loc.translate.set(pnt)
            ctrl_obj = control.Control(EYERING.__name__, self.version, self.side, self.side + '_' + EYERING.__name__)
            ctrl_obj.build(tmp_loc)
            self.data[tmp_loc.replace('_loc', '_ctrl')] = ctrl_obj
            pm.delete(tmp_loc)

            ctrl_obj.get_node('zro').visibility.set(0)
            nurbs.attach_obj_to_surface(ctrl_obj.get_node('con'), self.upLid_surf, rot=False)

            # handle pre matrtix connection
            pre_con = ctrl_obj.get_node('con_pre')
            sub_con = ctrl_obj.get_node('con')
            pm.disconnectAttr(sub_con.translate, pre_con.translate)
            pm.disconnectAttr(sub_con.rotate, pre_con.rotate)
            pm.disconnectAttr(sub_con.scale, pre_con.scale)

    def build_lo_ring(self):
        lolid = ['loRing_1_loc', 'loRing_2_loc', 'loRing_3_loc']

        for each in lolid:
            item = '{}_{}'.format(self.side, each)
            ctrl_name = item.replace('_loc', '_ctrl')
            item_node = pm.PyNode(item)
            ctrl_obj = control.Control(EYERING.__name__, self.version, self.side, self.side + '_' + EYERING.__name__)
            ctrl_obj.build(item_node)
            self.data[ctrl_name] = ctrl_obj

            # ctrl bind jnt
            self.lo_bind_jnts.append(ctrl_obj.get_node('bind'))

            # build connection to major
            lo_major = self.data[self.side + '_loRing_ctrl'].get_node('ctrl')
            sub_ctrl_ato = ctrl_obj.get_node('ato')

            con = pm.parentConstraint(lo_major, sub_ctrl_ato, mo=1)
            if item == self.side+'_loRing_2_loc':
                utility.eye_weight_constraints(con, sub_ctrl_ato, w=0)
            else:
                utility.eye_weight_constraints(con, sub_ctrl_ato)

        # build main bind joints on surface
        # bind_jnts = nurbs.obj_on_surface(self.side + '_loring', self.loLid_surf, rotation=False, joint=True)
        # pm.parent(bind_jnts, self.side + '_eyering_binds')
        pnts_on_surface = nurbs.get_vert_positons_on_surf(self.side + '_loring', self.loLid_surf)
        for i, pnt in enumerate(pnts_on_surface):
            tmp_loc_shape = pm.createNode('locator')
            tmp_loc = pm.rename(tmp_loc_shape.getParent(), self.side + '_loRing%d_sub_loc' % i)
            tmp_loc.translate.set(pnt)
            ctrl_obj = control.Control(EYERING.__name__, self.version, self.side, self.side + '_' + EYERING.__name__)
            ctrl_obj.build(tmp_loc)
            self.data[tmp_loc.replace('_loc', '_ctrl')] = ctrl_obj
            pm.delete(tmp_loc)

            ctrl_obj.get_node('zro').visibility.set(0)
            nurbs.attach_obj_to_surface(ctrl_obj.get_node('con'), self.loLid_surf, rot=False)
            # handle pre matrtix connection
            pre_con = ctrl_obj.get_node('con_pre')
            sub_con = ctrl_obj.get_node('con')
            pm.disconnectAttr(sub_con.translate, pre_con.translate)
            pm.disconnectAttr(sub_con.rotate, pre_con.rotate)
            pm.disconnectAttr(sub_con.scale, pre_con.scale)

    def build_corners(self):
        corner = ['ringIn_loc', 'ringOut_loc']
        for each in corner:
            item = '{}_{}'.format(self.side, each)
            ctrl_name = item.replace('_loc', '_ctrl')
            item_node = pm.PyNode(item)
            ctrl_obj = control.Control(EYERING.__name__, self.version, self.side, self.side + '_' + EYERING.__name__)
            ctrl_obj.build(item_node)
            self.data[ctrl_name] = ctrl_obj

            # self.up_bind_jnts.append(ctrl_obj.get_node('bind_jnt'))
            # self.lo_bind_jnts.append(ctrl_obj.get_node('bind_jnt'))
            self.up_bind_jnts.append(ctrl_obj.get_node('bind'))
            self.lo_bind_jnts.append(ctrl_obj.get_node('bind'))

        # skin surface to control bind joints
        pm.skinCluster(self.up_bind_jnts, self.upLid_surf, tsb=1)

        # skin surface to control bind joints
        pm.skinCluster(self.lo_bind_jnts, self.loLid_surf, tsb=1)

    def build_major(self):
        # up ring
        up_proxy_loc = '{}_{}'.format(self.side, 'upRing_loc')
        up_proxy_node = pm.PyNode(up_proxy_loc)

        ctrl_obj = control.Control(EYERING.__name__, self.version, self.side, self.side + '_' + EYERING.__name__)
        ctrl_obj.build(up_proxy_node)

        self.data[self.side+'_upRing_ctrl'] = ctrl_obj

        # lo ring
        lo_proxy_loc = '{}_{}'.format(self.side, 'loRing_loc')
        lo_proxy_node = pm.PyNode(lo_proxy_loc)

        ctrl_obj = control.Control(EYERING.__name__, self.version, self.side, self.side + '_' + EYERING.__name__)
        ctrl_obj.build(lo_proxy_node)

        self.data[self.side + '_loRing_ctrl'] = ctrl_obj

    def build_follow(self):
        # L_upLid_ctrl
        up_src_node = self.side + '_upLid_ctrl'
        if not up_src_node:
            return
        up_tgt_node = self.data.get(self.side+'_upRing_ctrl').get_node('ato')
        up_cons = pm.parentConstraint(up_src_node, up_tgt_node, mo=1)
        up_blend = utility.eye_weight_constraints(up_cons, up_tgt_node, 0.5)
        up_ring_ctrl = self.data.get(self.side + '_upRing_ctrl').get_node('ctrl')
        pm.addAttr(up_ring_ctrl, ln='follow', max=1, min=0, dv=0.5, k=1)
        pm.connectAttr(up_ring_ctrl.follow, up_blend.weight)

        # lo lid
        lo_src_node = self.side + '_loLid_ctrl'
        if not lo_src_node:
            return
        lo_tgt_node = self.data.get(self.side + '_loRing_ctrl').get_node('ato')
        lo_cons = pm.parentConstraint(lo_src_node, lo_tgt_node, mo=1)
        lo_blend = utility.eye_weight_constraints(lo_cons, lo_tgt_node, 0.5)
        lo_ring_ctrl = self.data.get(self.side + '_loRing_ctrl').get_node('ctrl')
        pm.addAttr(lo_ring_ctrl, ln='follow', max=1, min=0, dv=0.5, k=1)
        pm.connectAttr(lo_ring_ctrl.follow, lo_blend.weight)

    def setup_network(self):
        for key in self.data.keys():
            net = network.Network(EYERING.__name__)
            net.add_attr(key.replace('_ctrl', ''))
            net.set_connection(pm.PyNode(key), key.replace('_ctrl', ''))

    def get_sub_bind(self):
        sub_binds = []
        for key in self.data.keys():
            if key.endswith('_sub_ctrl'):
                inst = self.data.get(key)
                sub_binds.append(inst.get_node('bind'))
        return sub_binds