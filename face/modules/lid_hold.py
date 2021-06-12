"""
author : abhiraj KK - abhiajk@gmail.com
version : 0.1
date : 13-08-2019

base class to build lid setup for facial rig

"""

import pymel.core as pm

from lib import control
reload(control)

# later try to inherit

from lib import setDrivenKey as key

reload(key)


class Lid:
    def __init__(self):

        self.version = '0.1'

        if pm.objExists(Lid.__name__):
            self.part = pm.PyNode(Lid.__name__)
            self.bind_grp = pm.PyNode(Lid.__name__+'_bind')
            self.ctrl_grp = pm.PyNode(Lid.__name__ + '_ctrl')
            self.ctrl_grp = pm.PyNode(Lid.__name__ + '_pre')
        else:
            self.part = pm.createNode('transform', n=Lid.__name__)
            self.bind_grp = pm.createNode('transform', n=Lid.__name__+'_bind', p=self.part)
            self.ctrl_grp = pm.createNode('transform', n=Lid.__name__+'_ctrl', p=self.part)
            self.ctrl_grp = pm.createNode('transform', n=Lid.__name__ + '_pre', p=self.part)

        self.data = {}

    def get_lid_obj(self, name):
        return self.data.get(name, None)

    def get_node_from_obj(self, obj, suffix):
        return self.data.get(obj).get_node(suffix)

    def proxy(self):
        pass

    def build_controls(self):
        sel = pm.ls(sl=1)
        if not sel:
            raise RuntimeError("Please select Lid proxy loc")

        for each in sel:

            # side check
            name = each.name().replace('_loc', '')
            if name.startswith('L_'):
                side = 'L'
            elif name.startswith('R_'):
                side = 'R'
            else:
                side = 'M'

            # add ctrl
            ctrl_obj = control.Control(Lid.__name__, self.version, side, side + '_' + Lid.__name__)
            '''ctrl_obj.sphere(name+'_ctrl', 0.08)
            ctrl_obj.set_hierarchy(ctrl_obj.get_node('ctrl'))
            pm.matchTransform(ctrl_obj.get_node('cons'), each)
            self.data[name] = ctrl_obj'''
            ctrl_obj.build(each)
            self.data[name+'_ctrl'] = ctrl_obj

    def rig(self):
        # build control
        self.build_controls()

        # build rig
        for side in ['L_', 'R_']:
            # eyelid
            eyelid = ['lidsUpperDriver', 'lidsUpperDriver001', 'lidsUpperDriver002', 'lidsUpperDriver003',
                      'lidsLowerDriver', 'lidsLowerDriver001', 'lidsLowerDriver002', 'lidsLowerDriver003']

            self.build_setup(side, eyelid, base='lids', upper='lidsUpper', lower='lidsLower',
                             upper_driver='lidsUpperDriver', lower_driver='lidsLowerDriver')
            # eye ring
            eye_ring = ['lidsRingUpperDriver', 'lidsRingUpperDriver001', 'lidsRingUpperDriver002',
                        'lidsRingUpperDriver003', 'lidsRingLowerDriver', 'lidsRingLowerDriver001',
                        'lidsRingLowerDriver002', 'lidsRingLowerDriver003']

            self.build_setup(side, eye_ring, base='lids', upper='lidsRingUpper', lower='lidsRingLower',
                             upper_driver='lidsRingUpperDriver', lower_driver='lidsRingLowerDriver')

            pm.parent(self.get_node_from_obj(side+'lidsIn_ctrl', 'zro'),
                      self.get_node_from_obj(side+'lids_ctrl', 'nul'))

            pm.parent(self.get_node_from_obj(side + 'lidsOut_ctrl', 'zro'),
                      self.get_node_from_obj(side + 'lids_ctrl', 'nul'))

            pm.parent(self.get_node_from_obj(side + 'lidsIn_ctrl', 'zro_bind'),
                      self.get_node_from_obj(side + 'lids_ctrl', 'nul_bind'))

            pm.parent(self.get_node_from_obj(side + 'lidsOut_ctrl', 'zro_bind'),
                      self.get_node_from_obj(side + 'lids_ctrl', 'nul_bind'))

        # build rest <<<<< hold for now __)()()()
        self.build_blink_setup()
        self.set_lids_pc_weight()
        self.build_soft_eye_setup()
        self.add_z_attr()

    def build_setup(self, side, driver_list, base='lids', upper='lidsUpper', lower='lidsLower',
                    upper_driver='lidsUpperDriver', lower_driver='lidsLowerDriver'):

        # build lid rig
        base_null = self.get_node_from_obj(side + base+'_ctrl', 'nul')
        base_bind = self.get_node_from_obj(side + base+'_ctrl', 'nul_bind')

        for lid in driver_list:
            ctrl_obj = control.Control(Lid.__name__, self.version, side, side + Lid.__name__)
            ctrl_obj.hierarchy = ['con', 'ort', 'mir', 'pvt', 'ato', 'sdk', 'ofs', 'nul']
            ctrl_obj.pre_hierarchy = ['con', 'ort', 'mir', 'pvt']

            ctrl = pm.createNode('transform', n='{}{}{}'.format(side, lid, '_ctrl'))
            ctrl_obj.set_hierarchy(ctrl)
            pm.matchTransform(ctrl_obj.get_node('con'), base_null)
            pm.parent(ctrl_obj.get_node('con'), base_null)
            pm.parent(ctrl_obj.get_node('con_bind'), base_bind)
            self.data[side + lid] = ctrl_obj

        # set special hierarchy for lids
        pm.parent(self.get_node_from_obj(side + upper+'_ctrl', 'con'), base_null)
        pm.parent(self.get_node_from_obj(side + lower+'_ctrl', 'con'), base_null)

        pm.parent(self.get_node_from_obj(side + upper+'_ctrl', 'con_bind'), base_bind)
        pm.parent(self.get_node_from_obj(side + lower+'_ctrl', 'con_bind'), base_bind)

        # set
        for each in driver_list:
            item = side + each

            if each == upper_driver or each == lower_driver:
                pass
            else:
                if 'Upper' in item:
                    pm.parent(self.get_node_from_obj(item, 'con'),
                              self.get_node_from_obj(side + upper_driver, 'nul'))

                    pm.parent(self.get_node_from_obj(item, 'con_bind'),
                              self.get_node_from_obj(side + upper_driver, 'nul_bind'))
                else:
                    pm.parent(self.get_node_from_obj(item, 'con'),
                              self.get_node_from_obj(side + lower_driver, 'nul'))

                    pm.parent(self.get_node_from_obj(item, 'con_bind'),
                              self.get_node_from_obj(side + lower_driver, 'nul_bind'))
            # aim
            source_item = side + each.replace('Driver', '')+'_ctrl'
            source = self.get_node_from_obj(source_item, 'nul')
            ofs = self.get_node_from_obj(source_item, 'ofs')
            sdk = self.get_node_from_obj(source_item, 'sdk')
            auto = self.get_node_from_obj(source_item, 'ato')
            pivot = self.get_node_from_obj(source_item, 'pvt')
            mirror = self.get_node_from_obj(source_item, 'mir')
            target = self.get_node_from_obj(item, 'con')

            up_matrix = pm.createNode('multMatrix', n=target.name() + '_upVec_mm')
            source.matrix >> up_matrix.matrixIn[0]
            ofs.matrix >> up_matrix.matrixIn[1]
            sdk.matrix >> up_matrix.matrixIn[2]
            auto.matrix >> up_matrix.matrixIn[3]
            pivot.matrix >> up_matrix.matrixIn[4]
            mirror.worldMatrix[0] >> up_matrix.matrixIn[5]

            if side == 'R_':
                aim = [0, 0, -1]
            else:
                aim = [0, 0, 1]

            aim = pm.aimConstraint(source, target, mo=0, aimVector=aim,
                                   upVector=[0, 1, 0], worldUpType='objectrotation',
                                   n=target.name() + '_aim')
            up_matrix.matrixSum >> aim.worldUpMatrix

            # parent sub ctrl
            if each == upper_driver or each == lower_driver:
                pass
            else:
                '''
                if 'Upper' in item:
                    pm.parent(self.get_node_from_obj(source_item, 'zro'),
                              self.get_node_from_obj(side + upper_driver, 'nul'))
                    pm.parent(self.get_node_from_obj(source_item, 'zro_bind'),
                              self.get_node_from_obj(side + upper_driver, 'nul_bind'))
                else:
                    pm.parent(self.get_node_from_obj(source_item, 'zro'),
                              self.get_node_from_obj(side + lower_driver, 'nul'))
                    pm.parent(self.get_node_from_obj(source_item, 'zro_bind'),
                              self.get_node_from_obj(side + lower_driver, 'nul_bind'))'''

                # adjust upper-lower 001 and 003 to offset to have a arc
                tgt = pm.createNode('transform', p=base_null, n=side + each + '_tgt')
                pm.matchTransform(tgt, self.get_node_from_obj(side+each, 'con'))

                if 'Upper' in item:
                    pm.parent(self.get_node_from_obj(source_item, 'con'),
                              base_null)
                    pm.parent(self.get_node_from_obj(source_item, 'con_bind'),
                              base_bind)

                    # offset constraint
                    if 'RingUpper' in item:

                        '''cons = pm.parentConstraint(base_null,
                                                   self.get_node_from_obj(side + 'lidsRingUpperDriver', 'nul'),
                                                   self.get_node_from_obj(source_item, 'con'), mo=1)'''
                        cons = pm.parentConstraint(tgt,
                                                   self.get_node_from_obj(side + 'lidsRingUpperDriver', 'nul'),
                                                   self.get_node_from_obj(source_item, 'con'), mo=1)
                        self.data[source_item+'_pc'] = cons

                    else:
                        '''cons = pm.parentConstraint(base_null,
                                                   self.get_node_from_obj(side + 'lidsUpperDriver', 'nul'),
                                                   self.get_node_from_obj(source_item, 'con'), mo=1)'''
                        cons = pm.parentConstraint(tgt,
                                                   self.get_node_from_obj(side + 'lidsUpperDriver', 'nul'),
                                                   self.get_node_from_obj(source_item, 'con'), mo=1)
                        self.data[source_item + '_pc'] = cons
                else:
                    pm.parent(self.get_node_from_obj(source_item, 'con'),
                              base_null)
                    pm.parent(self.get_node_from_obj(source_item, 'con_bind'),
                              base_bind)

                    # offset constraint
                    if 'RingLower' in item:
                        cons = pm.parentConstraint(tgt,
                                                   self.get_node_from_obj(side + 'lidsRingLowerDriver', 'nul'),
                                                   self.get_node_from_obj(source_item, 'con'), mo=1)
                        self.data[source_item + '_pc'] = cons

                    else:
                        cons = pm.parentConstraint(tgt,
                                                   self.get_node_from_obj(side + 'lidsLowerDriver', 'nul'),
                                                   self.get_node_from_obj(source_item, 'con'), mo=1)
                        self.data[source_item + '_pc'] = cons

    def set_lids_pc_weight(self):

        for side in ['L_', 'R_']:
            # set offset constraints weight
            pm.setAttr(self.data[side+'lidsUpper001_ctrl_pc']+'.%slidsUpperDriver001_tgtW0' % side, 0.25)
            pm.setAttr(self.data[side + 'lidsUpper001_ctrl_pc'] + '.%slidsUpperDriver_nulW1' % side, 0.75)

            pm.setAttr(self.data[side + 'lidsUpper002_ctrl_pc'] + '.%slidsUpperDriver002_tgtW0' % side, 0.0)
            pm.setAttr(self.data[side + 'lidsUpper002_ctrl_pc'] + '.%slidsUpperDriver_nulW1' % side, 1.0)

            pm.setAttr(self.data[side + 'lidsUpper003_ctrl_pc'] + '.%slidsUpperDriver003_tgtW0' % side, 0.25)
            pm.setAttr(self.data[side + 'lidsUpper003_ctrl_pc'] + '.%slidsUpperDriver_nulW1' % side, 0.75)

            pm.setAttr(self.data[side + 'lidsLower001_ctrl_pc'] + '.%slidsLowerDriver001_tgtW0' % side, 0.25)
            pm.setAttr(self.data[side + 'lidsLower001_ctrl_pc'] + '.%slidsLowerDriver_nulW1' % side, 0.75)

            pm.setAttr(self.data[side + 'lidsLower002_ctrl_pc'] + '.%slidsLowerDriver002_tgtW0' % side, 0.0)
            pm.setAttr(self.data[side + 'lidsLower002_ctrl_pc'] + '.%slidsLowerDriver_nulW1' % side, 1.0)

            pm.setAttr(self.data[side + 'lidsLower003_ctrl_pc'] + '.%slidsLowerDriver003_tgtW0' % side, 0.25)
            pm.setAttr(self.data[side + 'lidsLower003_ctrl_pc'] + '.%slidsLowerDriver_nulW1' % side, 0.75)
            # lower
            pm.setAttr(self.data[side + 'lidsRingUpper001_ctrl_pc'] + '.%slidsRingUpperDriver001_tgtW0' % side, 0.25)
            pm.setAttr(self.data[side + 'lidsRingUpper001_ctrl_pc'] + '.%slidsRingUpperDriver_nulW1' % side, 0.75)

            pm.setAttr(self.data[side + 'lidsRingUpper002_ctrl_pc'] + '.%slidsRingUpperDriver002_tgtW0' % side, 0.0)
            pm.setAttr(self.data[side + 'lidsRingUpper002_ctrl_pc'] + '.%slidsRingUpperDriver_nulW1' % side, 1.0)

            pm.setAttr(self.data[side + 'lidsRingUpper003_ctrl_pc'] + '.%slidsRingUpperDriver003_tgtW0' % side, 0.25)
            pm.setAttr(self.data[side + 'lidsRingUpper003_ctrl_pc'] + '.%slidsRingUpperDriver_nulW1' % side, 0.75)

            pm.setAttr(self.data[side + 'lidsRingLower001_ctrl_pc'] + '.%slidsRingLowerDriver001_tgtW0' % side, 0.25)
            pm.setAttr(self.data[side + 'lidsRingLower001_ctrl_pc'] + '.%slidsRingLowerDriver_nulW1' % side, 0.75)

            pm.setAttr(self.data[side + 'lidsRingLower002_ctrl_pc'] + '.%slidsRingLowerDriver002_tgtW0' % side, 0.0)
            pm.setAttr(self.data[side + 'lidsRingLower002_ctrl_pc'] + '.%slidsRingLowerDriver_nulW1' % side, 1.0)

            pm.setAttr(self.data[side + 'lidsRingLower003_ctrl_pc'] + '.%slidsRingLowerDriver003_tgtW0' % side, 0.25)
            pm.setAttr(self.data[side + 'lidsRingLower003_ctrl_pc'] + '.%slidsRingLowerDriver_nulW1' % side, 0.75)

    def build_blink_setup(self):
        upper_blink = 0.20
        lower_blink = 0.050
        upper_blink_height = 0.5
        lower_blink_height = 0.5

        # add Attr
        for side in ['L_', 'R_']:
            upper_obj = self.data[side+'lidsUpper_ctrl']
            #upper_node = upper_obj.get_node('ctrl')
            upper_node = self.get_node_from_obj(side+'lidsUpper_ctrl', 'ctrl')
            pm.addAttr(upper_node, ln='blink', min=-100, max=100, k=1)
            pm.addAttr(upper_node, ln='blinkHeight', min=0, max=100, k=1)

            upper_driven = upper_obj.get_node('ato')
            key.set_driven_key(upper_node, 'blink', upper_driven, 'ty')
            upper_node.blink.set(100)
            upper_driven.ty.set(upper_blink*-1)
            key.set_driven_key(upper_node, 'blink', upper_driven, 'ty')
            upper_node.blink.set(0)

            upper_node.blink.set(-100)
            upper_driven.ty.set(upper_blink)
            key.set_driven_key(upper_node, 'blink', upper_driven, 'ty')
            upper_node.blink.set(0)

            lower_obj = self.data[side+'lidsLower_ctrl']
            lower_driven = lower_obj.get_node('ato')
            key.set_driven_key(upper_node, 'blink', lower_driven, 'ty')
            upper_node.blink.set(100)
            lower_driven.ty.set(lower_blink*-1)
            key.set_driven_key(upper_node, 'blink', lower_driven, 'ty')
            upper_node.blink.set(0)

            upper_node.blink.set(-100)
            lower_driven.ty.set(lower_blink)
            key.set_driven_key(upper_node, 'blink', lower_driven, 'ty')
            upper_node.blink.set(0)

            # blink height
            blink_height = pm.createNode('remapValue', n=upper_node.name().replace('_ctrl', '_rmv'))
            upper_node.blinkHeight >> blink_height.inputValue
            blink_height.inputMax.set(100)

            upper_height_blend = pm.createNode('blendTwoAttr', n=upper_node.name().replace('_ctrl', '_bta'))
            blink_height.outValue >> upper_height_blend.attributesBlender
            upper_height_blend.input[1].set(0)
            pm.connectAttr('%slidsUpper_ato_translateY.output' % side, upper_height_blend.input[0])
            upper_height_blend.output >> upper_driven.ty

            lower_height_blend = pm.createNode('blendTwoAttr', n=upper_node.name().replace('Upper_ctrl', 'Lower_bta'))
            blink_height.outValue >> lower_height_blend.attributesBlender
            lower_height_blend.input[1].set(0)
            pm.connectAttr('%slidsLower_ato_translateY.output' % side, lower_height_blend.input[0])
            lower_height_blend.output >> lower_driven.ty

            # lower blink height
            lower_height = pm.createNode('remapValue', n=lower_driven.name().replace('_ato', '_rmv'))
            upper_node.blinkHeight >> lower_height.inputValue
            lower_height.inputMax.set(100)

            pm.connectAttr('%slidsUpper_ato_translateY.output' % side,
                           lower_height_blend.input[1])

    def build_soft_eye_setup(self):
        for side in ['L_', 'R_']:

            attr_node_obj = self.data[side+'eye_ctrl']
            attr_node = attr_node_obj.get_node('ctrl')
            node_null = attr_node_obj.get_node('nul')
            node_cons = attr_node_obj.get_node('con')

            pm.addAttr(attr_node, ln='LidsHorizontalFollow', dv=5, k=1)
            pm.addAttr(attr_node, ln='LidsVerticalFollow', dv=35, k=1)

            driver_node_obj = self.data[side+'eyeDriver_ctrl']
            driver_node = driver_node_obj.get_node('ato')

            if side == 'R_':
                aim = [0, 0, -1]
            else:
                aim = [0, 0, 1]
            pm.aimConstraint(node_null, driver_node, wut='objectrotation', wuo=node_null, wu=(0, 1, 0), aim=aim,
                             u=(0, 1, 0), mo=0)

            lidsUpperDriver_obj = self.data[side+'lidsUpperDriver']
            lidsUpperDriver_sdk = lidsUpperDriver_obj.get_node('sdk')

            lidsLowerDriver_obj = self.data[side + 'lidsLowerDriver']
            lidsLowerDriver_sdk = lidsLowerDriver_obj.get_node('sdk')

            horizontal = pm.createNode('pairBlend', n=side+'LidsHorizontalFollow_PB')
            horizontal_rmv = pm.createNode('remapValue', n=side+'LidsHorizontalFollow_rmv')
            attr_node.LidsHorizontalFollow >> horizontal_rmv.inputValue
            horizontal_rmv.inputMax.set(100)

            horizontal_rmv.outValue >> horizontal.weight
            driver_node.rotate >> horizontal.inRotate2

            horizontal.outRotateY >> lidsUpperDriver_sdk.rotateY

            # mdl for lower to have flip
            neg_mdl = pm.createNode('multDoubleLinear', n=side+'LidsHorizontalFollow_neg_mdl')
            horizontal.outRotateY >> neg_mdl.input1
            neg_mdl.input2.set(-1)

            neg_mdl.output >> lidsLowerDriver_sdk.rotateY

            vertical = pm.createNode('pairBlend', n=side + 'LidsVerticalFollow_PB')
            vertical_rmv = pm.createNode('remapValue', n=side + 'LidsVerticalFollow_rmv')
            attr_node.LidsVerticalFollow >> vertical_rmv.inputValue
            vertical_rmv.inputMax.set(100)

            vertical_rmv.outValue >> vertical.weight
            driver_node.rotate >> vertical.inRotate2

            vertical.outRotateX >> lidsUpperDriver_sdk.rotateX

            # lower neg flip
            neg_mdl = pm.createNode('multDoubleLinear', n=side + 'LidsVerticalFollow_neg_mdl')
            vertical.outRotateX >> neg_mdl.input1
            neg_mdl.input2.set(-1)

            neg_mdl.output >> lidsLowerDriver_sdk.rotateX

            m_eye_obj = self.data['M_eye_ctrl']
            m_eye_node = m_eye_obj.get_node('nul')

            pm.parentConstraint(m_eye_node, node_cons, mo=1)

    def build_strech_squash(self):

        for side in ['L_', 'R_']:
            #'L_eyeDriver_loc'

            # add ctrl
            ctrl_obj = control.Control(Lid.__name__, self.version, side, side + '_' + Lid.__name__)
            ctrl_obj.sphere(side+'eyeDriver' + '_ctrl', 0.08)
            ctrl_obj.set_hierarchy(ctrl_obj.get_node('ctrl'))
            pm.matchTransform(ctrl_obj.get_node('cons'), side+'eyeDriver_loc')
            self.data[side+'eyeDriver'] = ctrl_obj

    def build_bind_jnts(self, cvs, name='loLid', root='L_eyeLidBase', crv='L_loLid_crvShape'):

        # cvs = pm.ls(sl=1, fl=1)

        node = pm.createNode('nearestPointOnCurve')

        pm.connectAttr(crv + '.worldSpace', node + '.inputCurve')

        for i, each in enumerate(cvs):
            pos = pm.xform(each, q=1, t=1, ws=1)

            node.inPosition.set(pos)
            u = node.parameter.get()

            poci = pm.createNode('pointOnCurveInfo', n=name + '%d_poci' % i)
            poci.parameter.set(node.parameter.get())

            pm.connectAttr(crv + '.worldSpace', poci + '.inputCurve')

            # node.parameter >> poci.parameter

            drv = pm.createNode('transform', n=name + '%d_bind_grp' % i)

            poci.position >> drv.translate

            jnt = pm.createNode('joint', p=root, n=name + '%d_bind' % i)

            pm.matchTransform(jnt, drv)

    def master_corners(self):
        pass

    def add_z_attr(self):
        for each in self.data.keys():

            if each.endswith('_ctrl'):
                pm.addAttr(each, ln='Z', k=1)
                mdl = pm.createNode('multDoubleLinear', n=each+'_Z_mdl')
                pm.connectAttr(each+'.Z',  mdl.input1)
                mdl.input2.set(0.1)

                if each.startswith('R_'):
                    mdl.input2.set(-0.1)

                if 'Lower' in each:
                    val = mdl.input2.get() * -1.0
                    mdl.input2.set(val)

                pm.connectAttr(mdl.output, each+'.tz')
                pm.setAttr(each+'.tz', l=1, k=0)

            if '_ctrl' not in each:
                pm.connectAttr(each.replace('Driver', '')+'_ctrl.tz',
                               each+'_con.tz')

                if 'Lower' in each:
                    neg_mdl = pm.createNode('multDoubleLinear', n=each + '_negZ_mdl')
                    neg_mdl.input2.set(-1)
                    pm.connectAttr(each.replace('Driver', '') + '_ctrl.tz', neg_mdl.input1)

                    pm.connectAttr(neg_mdl.output, each + '_con.tz', f=1)