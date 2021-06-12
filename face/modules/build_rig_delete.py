import pymel.core as pm

import eyeRing

reload(eyeRing)

import lids
reload(lids)

import brow
reload(brow)

from lib import control
reload(control)

from lib import skin
reload(skin)

import eyes
reload(eyes)


class RIG:
    def __init__(self):
        self.version = '0.1'
        self.data = {}
        self.rig_inst = {}

    """First layer"""
    # lids
    def build_eye_lid(self):
        #
        item_node = pm.PyNode('M_eyeHold_loc')
        item_name = 'M_eyeHold_ctrl'
        ctrl_obj = control.Control('eyeHold', self.version, 'M', 'M' + '_' + RIG.__name__)
        ctrl_obj.build(item_node)
        self.data[item_name] = ctrl_obj

        #
        l_eye_lid = lids.LID('L')
        l_eye_lid.build()
        self.rig_inst['L_eyeLid'] = l_eye_lid

        r_eye_lid = lids.LID('R')
        r_eye_lid.build()
        self.rig_inst['R_eyeLid'] = r_eye_lid

    # build_ring
    def build_eye_ring(self):
        l_eye_ring = eyeRing.EYERING('L')
        l_eye_ring.build()
        self.rig_inst['L_eyeRing'] = l_eye_ring

        r_eye_ring = eyeRing.EYERING('R')
        r_eye_ring.build()
        self.rig_inst['R_eyeRing'] = r_eye_ring

    """second layer"""

    # brow
    def build_brow(self):

        #
        item_node = pm.PyNode('M_browHold_loc')
        item_name = 'M_browHold_ctrl'
        ctrl_obj = control.Control('brow', self.version, 'M', 'M' + '_' + RIG.__name__)
        ctrl_obj.build(item_node)
        self.data[item_name] = ctrl_obj
        #
        brow_inst = brow.BROW('L')
        brow_inst.build()
        self.rig_inst['L_brow'] = brow_inst

        #
        brow_inst = brow.BROW('R')
        brow_inst.build()
        self.rig_inst['R_brow'] = brow_inst

    def build_eyes(self):
        eye_inst = eyes.EYES('L')
        eye_inst.build()

        eye_inst = eyes.EYES('R')
        eye_inst.build()

        eye_inst.build_mid()


    # bind
    def bind_geo(self, head, l_eye, r_eye, brow):
        # need to query from UI later

        '''head_geo = 'face_skin_localRig'
        L_eye_geo = 'L_pupil_geo'
        R_eye_geo = 'R_pupil_geo'
        brow_geo = 'brow_geo'
        '''

        head_geo = head
        L_eye_geo = l_eye
        R_eye_geo = r_eye
        brow_geo = brow

        if self.data.get('M_eyeHold_ctrl'):
            if pm.objExists('eyeLid_skin'):
                return

            # first layer skin
            eye_skin = pm.skinCluster(self.data.get('M_eyeHold_ctrl').get_node('bind'), head_geo, tsb=1,
                                      dr=4, normalizeWeights=1, weightDistribution=0, mi=4,
                                      n='eyeLid_skin')

            # add first layer bind joints
            l_eye_joints = self.rig_inst.get('L_eyeLid').get_sub_bind()
            r_eye_joints = self.rig_inst.get('R_eyeLid').get_sub_bind()

            l_eye_ring_joints = self.rig_inst.get('L_eyeRing').get_sub_bind()
            r_eye_ring_joints = self.rig_inst.get('R_eyeRing').get_sub_bind()

            pm.skinCluster(eye_skin, e=1, dr=4, lw=1, normalizeWeights=1, wt=0.0, ai=l_eye_joints)
            pm.skinCluster(eye_skin, e=1,  dr=4, lw=1, normalizeWeights=1,  wt=0.0, ai=r_eye_joints)
            pm.skinCluster(eye_skin, e=1,  dr=4, lw=1, normalizeWeights=1, wt=0.0, ai=l_eye_ring_joints)
            pm.skinCluster(eye_skin, e=1,  dr=4, lw=1, normalizeWeights=1, wt=0.0, ai=r_eye_ring_joints)

            skin.connect_pre_matrix(eye_skin)

        # build second layer skin
        if self.data.get('M_browHold_ctrl'):
            if pm.objExists('brow_skin'):
                return
            brow_skin_geo = pm.duplicate(head_geo, n='brow_skin_geo')

            brow_skin = pm.skinCluster(self.data.get('M_browHold_ctrl').get_node('bind'), brow_skin_geo, tsb=1,
                                       dr=4, normalizeWeights=1, weightDistribution=0, mi=4,
                                       n='brow_skin')

            # add second layer bind joints
            brow_bind_joints = self.rig_inst.get('L_brow').get_bind()
            pm.skinCluster(brow_skin, e=1,  dr=4, lw=1, normalizeWeights=1, wt=0.0, ai=brow_bind_joints)

            brow_bind_joints = self.rig_inst.get('R_brow').get_bind()
            pm.skinCluster(brow_skin, e=1,  dr=4, lw=1, normalizeWeights=1, wt=0.0, ai=brow_bind_joints)

            skin.connect_pre_matrix(brow_skin)

    def first_layer(self, sides, head, l_eye, r_eye, lid=True, ring=True, eye=True):
        #
        item_node = pm.PyNode('M_eyeHold_loc')
        item_name = 'M_eyeHold_ctrl'
        ctrl_obj = control.Control('eyeHold', self.version, 'M', 'M' + '_' + RIG.__name__)
        ctrl_obj.build(item_node)
        self.data[item_name] = ctrl_obj

        for side in sides:
            #
            if lid:
                eye_lid = lids.LID(side)
                eye_lid.build()
                self.rig_inst[side+'_eyeLid'] = eye_lid
            if ring:
                eye_ring = eyeRing.EYERING(side)
                eye_ring.build()
                self.rig_inst[side+'_eyeRing'] = eye_ring
            if eye and lid:
                eye_inst = eyes.EYES(side)
                eye_inst.build()
                if side == 'L':
                    eye_inst.eye_squash(head, l_eye)
                elif side == 'R':
                    eye_inst.eye_squash(head, r_eye)
        if sides == 'LR':
            eye_inst = eyes.EYES('M')
            eye_inst.build_mid()

        # self.bind_geo()
        eye_master_grp = pm.createNode('transform', n='eyes')
        eye_grps = ['eyehold_ctrl', 'eyehold_bind', 'eyehold_pre', 'lid_ctrl', 'lid_pre', 'lid_bind', 'lid_sys',
                    'eyering_ctrl', 'eyering_bind', 'eyering_pre', 'eyering_sys', 'eyes_ctrl', 'eyes_pre', 'eyes_bind']
        pm.parent(eye_grps, eye_master_grp)
        pm.parent('L_uplid_sub_aim_grp', 'R_uplid_sub_aim_grp', 'L_lolid_sub_aim_grp', 'R_lolid_sub_aim_grp',
                  'lid_sys')

    def second_layer(self, sides):
        #
        item_node = pm.PyNode('M_browHold_loc')
        item_name = 'M_browHold_ctrl'
        ctrl_obj = control.Control('brow', self.version, 'M', 'M' + '_' + RIG.__name__)
        ctrl_obj.build(item_node)
        self.data[item_name] = ctrl_obj

        for side in sides:
            #
            brow_inst = brow.BROW(side)
            brow_inst.build()
            self.rig_inst[side+'_brow'] = brow_inst
        # self.bind_geo()
        brow_master_grp = pm.createNode('transform', n='brows')
        brow_grps = ['brow_ctrl', 'brow_bind', 'brow_pre', 'brow_sys']
        pm.parent(brow_grps, brow_master_grp)

    @staticmethod
    def _clean():
        # more clean up hirearchy
        eye_master_grp = pm.createNode('transform', n='eyes')
        eye_grps = ['eyehold_ctrl', 'eyehold_bind', 'eyehold_pre', 'lid_ctrl', 'lid_pre', 'lid_bind', 'lid_sys',
                    'eyering_ctrl', 'eyering_bind', 'eyering_pre', 'eyering_sys']
        pm.parent(eye_grps, eye_master_grp)
        pm.parent('L_uplid_sub_aim_grp', 'R_uplid_sub_aim_grp', 'L_lolid_sub_aim_grp', 'R_lolid_sub_aim_grp','lid_sys')

        brow_master_grp = pm.createNode('transform', n='brows')
        brow_grps = ['brow_ctrl', 'brow_bind', 'brow_pre', 'brow_sys']
        pm.parent(brow_grps, brow_master_grp)

