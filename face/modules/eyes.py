import pymel.core as pm

#from lib import controls as ctrl
from lib import control
reload(control)

from lib.OBB.api import OBB


class EYES:
    def __init__(self, side):
        self.side = side
        self.data = {}
        self.version = '0.1'

    def build(self):
        self.build_controls()
        self.connect_eyes()
        self.eye_lids_follow()
        # self.eye_squash()

    def build_controls(self):
        proxy_loc = [self.side+'_lidOrigin_loc', self.side+'_eye_loc']

        for each in proxy_loc:
            if pm.objExists(each):

                each = pm.PyNode(each)
                # side check
                name = each.name().replace('_loc', '')
                item = each.name().replace('_loc', '_ctrl')
                if name.startswith('L_'):
                    side = 'L'
                elif name.startswith('R_'):
                    side = 'R'
                else:
                    side = 'M'

                ctrl_obj = control.Control(EYES.__name__, self.version, side, side + '_' + EYES.__name__)
                ctrl_obj.build(each)
                self.data[item] = ctrl_obj

        # origin fk ctrl
        eye_fk_loc = pm.createNode('locator')
        node = pm.rename(eye_fk_loc.getParent(), self.side+'_eyeFK_loc')
        pm.matchTransform(eye_fk_loc.getParent(), self.side+'_lidOrigin_loc')

        ctrl_obj = control.Control(EYES.__name__, self.version, side, side + '_' + EYES.__name__)
        ctrl_obj.build(node)
        self.data[self.side+'_eyeFK_ctrl'] = ctrl_obj
        pm.delete(eye_fk_loc.getParent())

        # fix eye orientation using OBB

    def build_mid(self):
        m_eye_loc = pm.createNode('locator')
        m_eye_loc = m_eye_loc.getParent()
        pm.rename(m_eye_loc, 'M_eye_loc')
        pm.delete(pm.pointConstraint('L_eye_ctrl', 'R_eye_ctrl', 'M_eye_loc', mo=0))
        ctrl_obj = control.Control(EYES.__name__, self.version, 'M', 'M' + '_' + EYES.__name__)
        ctrl_obj.build(m_eye_loc)
        self.data['M_eye_ctrl'] = ctrl_obj
        pm.parentConstraint('M_eye_ctrl', 'L_eye_ctrl_con', mo=True)
        pm.parentConstraint('M_eye_ctrl', 'R_eye_ctrl_con', mo=True)
        pm.delete(m_eye_loc)

    def connect_eyes(self):
        ctrl = self.data.get(self.side+'_eye_ctrl').get_node('ctrl')
        ato = self.data.get(self.side+'_eyeFK_ctrl').get_node('ato')

        pm.aimConstraint(ctrl, ato, aimVector=[0, 0, 1], upVector=[0, 1, 0], worldUpType='objectrotation',
                         worldUpVector=[0, 1, 0], worldUpObject=ctrl, mo=1)

    def eye_lids_follow(self):
        fk_ctrl = self.data.get(self.side+'_eyeFK_ctrl').get_node('nul')
        fk = self.data.get(self.side+'_eyeFK_ctrl').get_node('ctrl')

        pm.addAttr(fk, ln='lidsFolllow', dv=25, k=True)
        rmv = pm.createNode('remapValue', n=self.side+'_eyeLid_follow_rmv')
        fk.lidsFolllow >> rmv.inputValue
        rmv.inputMax.set(100)

        up_follow_grp = pm.createNode('transform', n=self.side+'_upLid_follow_tgt')
        lo_follow_grp = pm.createNode('transform', n=self.side + '_loLid_follow_tgt')

        pm.matchTransform(up_follow_grp, self.side+'_upLid_ctrl')
        pm.matchTransform(lo_follow_grp, self.side + '_loLid_ctrl')

        pm.parent(up_follow_grp, lo_follow_grp, fk_ctrl)

        up_con = pm.pointConstraint(up_follow_grp, self.side+'_upLid_ctrl_piv', mo=1)
        lo_con = pm.pointConstraint(lo_follow_grp, self.side + '_loLid_ctrl_piv', mo=1)

        pm.disconnectAttr(up_con.constraintTranslate.constraintTranslateX, self.side+'_upLid_ctrl_piv.tx')
        pm.disconnectAttr(up_con.constraintTranslate.constraintTranslateY, self.side + '_upLid_ctrl_piv.ty')
        pm.disconnectAttr(up_con.constraintTranslate.constraintTranslateZ, self.side + '_upLid_ctrl_piv.tz')

        pm.disconnectAttr(lo_con.constraintTranslate.constraintTranslateX, self.side + '_loLid_ctrl_piv.tx')
        pm.disconnectAttr(lo_con.constraintTranslate.constraintTranslateY, self.side + '_loLid_ctrl_piv.ty')
        pm.disconnectAttr(lo_con.constraintTranslate.constraintTranslateZ, self.side + '_loLid_ctrl_piv.tz')

        up_blend = pm.createNode('blendWeighted', n=self.side+'_upLid_ato_bw')
        up_blend.weight[0].set(1)
        up_blend.weight[1].set(1)
        rmv.outValue >> up_blend.weight[1]
        in_con = pm.listConnections(self.side+'_upLid_ctrl_ato.ty')

        pm.connectAttr(in_con[0]+'.outValueY', up_blend.input[0])
        pm.connectAttr(up_con.constraintTranslate.constraintTranslateY, up_blend.input[1])

        pm.connectAttr(up_blend.output, self.side + '_upLid_ctrl_ato.ty', f=1)

        lo_blend = pm.createNode('blendWeighted', n=self.side + '_loLid_ato_bw')
        lo_blend.weight[0].set(1)
        lo_blend.weight[1].set(1)
        rmv.outValue >> lo_blend.weight[1]
        in_con = pm.listConnections(self.side + '_loLid_ctrl_ato.ty')

        pm.connectAttr(in_con[0]+'.outValueY', lo_blend.input[0])
        pm.connectAttr(lo_con.constraintTranslate.constraintTranslateY, lo_blend.input[1])

        pm.connectAttr(lo_blend.output, self.side + '_loLid_ctrl_ato.ty', f=1)

    def eye_squash(self, head, eye):
        geo = head
        eye_geo = eye

        ctrl = self.data.get(self.side + '_eye_ctrl').get_node('ctrl')
        eye_fk_con = self.data[self.side + '_eyeFK_ctrl'].get_node('con')
        eye_fk_ort = self.data[self.side + '_eyeFK_ctrl'].get_node('ort')
        eye_fk_ato = self.data[self.side + '_eyeFK_ctrl'].get_node('ato')

        # remove aim constraint
        aim = eye_fk_ato.rotateX.listConnections(type=['aimConstraint'])[0]
        pm.delete(aim)

        # fix eye fk orientation using OBB method
        mesh = eye

        if len(mesh) == 0:
            raise RuntimeError("Nothing selected!")

        obbBoundBoxPnts = OBB.from_points(mesh)
        obbCube = pm.polyCube(
            constructionHistory=False, name="pointMethod_GEO")[0]
        pm.xform(obbCube, matrix=obbBoundBoxPnts.matrix)

        pm.matchTransform(eye_fk_con, obbCube)
        eye_fk_ort.rotate.set(-90, -90, 0)
        eye_fk_con.scale.set(1.0, 1.0, 1.0)
        if self.side == 'R':
            print "in >>>"
            eye_fk_con.scale.set(-1.0, 1.0, 1.0)
            eye_fk_ort.rotate.set(-90, 90, 0)
        # redo aim
        self.connect_eyes()
        pm.delete(obbCube)

        eye_fk = self.data[self.side+'_eyeFK_ctrl'].get_node('ctrl')
        tmp_loc = pm.createNode('locator')
        pm.matchTransform(tmp_loc.getParent(), eye_fk)
        pm.rename(tmp_loc.getParent(), self.side+'_eyeSocket_loc')

        ctrl_obj = control.Control(EYES.__name__, self.version, self.side, self.side + '_' + EYES.__name__)
        ctrl_obj.build(tmp_loc.getParent())
        self.data[self.side+'_eyeSocket_ctrl'] = ctrl_obj

        socket_fk_con = ctrl_obj.get_node('con')
        socket_fk_ort = ctrl_obj.get_node('ort')
        # socket_fk_ort.rotate.set(-90, -90, 0)
        # socket_fk_con.scale.set(1.0, 1.0, 1.0)
        if self.side == 'R':
            socket_fk_con.scale.set(-1.0, 1.0, 1.0)
            socket_fk_ort.rotate.set(-180, 0, 0)

        pm.select(cl=1)
        cls = pm.cluster(wn=[ctrl_obj.get_node('nul'), ctrl_obj.get_node('nul')], n=self.side+'_eyeSocket_cls')[0]
        pm.cluster(cls, e=1, g=geo)
        pm.cluster(cls, e=1, g=eye_geo)

        ctrl_obj.get_node('piv').parentInverseMatrix[0] >> cls.bindPreMatrix

        pm.delete(tmp_loc.getParent())

    def build_eye_attributes(self):
        pass

