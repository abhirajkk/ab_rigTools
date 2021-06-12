"""
author : abhiraj KK - abhiajk@gmail.com
version : 0.1
date : 13-08-2019

base class to build BROW setup for facial rig

"""
import pymel.core as pm
from lib import setDrivenKey as key
reload(key)

from lib import control
reload(control)
# try inherit from control

from lib import network
reload(network)


class BROW:
    def __init__(self, side):

        self.version = '0.1'
        self.side = side
        self.brow_data = {}
        self.template = ['browIn_loc', 'browSubIn_loc', 'browMid_loc', 'browSubOut_loc', 'browOut_loc',
                         'brow_loc']

    def proxy(self):
        pass

    def build(self):
        """
        build BROW rig
        :param : None
        :return: None
        """
        self.build_controls()
        self.drive_sub_ctrls()
        self.set_sliding()
        self.set_brow_main()
        self.build_mid_brow()
        # self.average_mid_brow()
        # self.add_z_attr()
        self.setup_network()

    def build_controls(self):
        sel = [self.side + '_' + each for each in self.template]

        if not sel:
            return
        for each in sel:

            if pm.objExists(each):

                each = pm.PyNode(each)
                # side check
                name = each.name().replace('_loc', '')
                item = each.name().replace('_loc', '_ctrl')

                ctrl_obj = control.Control(BROW.__name__, self.version, self.side, self.side + '_' + BROW.__name__)

                ctrl_obj.hierarchy = ['zro', 'con', 'ort', 'mir', 'piv', 'riv', 'ato', 'drn', 'ofs', 'nul']

                ctrl_obj.build(each)

                self.brow_data[item] = ctrl_obj

    def drive_sub_ctrls(self):

        # note can make use of the instance from self.data
        drivers = ['_browIn_ctrl', '_browMid_ctrl', '_browOut_ctrl']
        drivens = ['_browSubIn_ctrl_drn', '_browSubOut_ctrl_drn']

        driverA = pm.PyNode('{}{}'.format(self.side, drivers[0]))
        driverB = pm.PyNode('{}{}'.format(self.side, drivers[1]))
        driverC = pm.PyNode('{}{}'.format(self.side, drivers[2]))

        drivenA = pm.PyNode('{}{}'.format(self.side, drivens[0]))
        drivenB = pm.PyNode('{}{}'.format(self.side, drivens[1]))

        # A
        pma_a = pm.createNode('plusMinusAverage', n=drivenA.name()+'_pma')
        pma_a.operation.set(3)
        driverA.t >> pma_a.input3D[0]
        driverB.t >> pma_a.input3D[1]
        pma_a.output3D >> drivenA.t

        # B
        pma_b = pm.createNode('plusMinusAverage', n=drivenB.name() + '_pma')
        pma_b.operation.set(3)
        driverB.t >> pma_b.input3D[0]
        driverC.t >> pma_b.input3D[1]
        pma_b.output3D >> drivenB.t

    # setup sliding effect by setting SDK
    def set_sliding(self):
        # 'M_brow_ctrl': 'M_brow_u_direction_crvShape',
        slide_items = {
                       'browIn_ctrl': '%s_browIn_u_direction_crvShape' % self.side,
                       'browMid_ctrl': '%s_browMid_u_direction_crvShape' % self.side,
                       'browOut_ctrl': '%s_browOut_u_direction_crvShape' % self.side,
                       }

        v_crv = '%s_brow_v_direction_crvShape' % self.side

        for item in slide_items.keys():
            key.set_drivenKey_from_curve(slide_items[item], self.side + '_' + item, "ty",
                                         self.side + '_' + item+'_ato', "tz")

            key.set_drivenKey_from_curve(v_crv, self.side + '_' + item, "tx",
                                         self.side + '_' + item+'_ato', "tz")

        # set BROW sub ctrl sliding
        driver_a = ['_browIn_ctrl_ato', '_browMid_ctrl_ato']
        driver_b = ['_browMid_ctrl_ato', '_browOut_ctrl_ato']

        driven_a = '_browSubIn_ctrl_ato'
        driven_b = '_browSubOut_ctrl_ato'

        bw_a = pm.createNode('blendWeighted', n=self.side+driven_a+'_bw')
        pm.connectAttr('{}{}.{}'.format(self.side, driver_a[0], 'tz'), bw_a.input[0])
        pm.connectAttr('{}{}.{}'.format(self.side, driver_a[1], 'tz'), bw_a.input[1])
        bw_a.weight[0].set(0.5)
        bw_a.weight[1].set(0.5)
        pm.connectAttr(bw_a.output, '{}{}.{}'.format(self.side, driven_a, 'tz'))

        bw_b = pm.createNode('blendWeighted', n=self.side + driven_b + '_bw')
        pm.connectAttr('{}{}.{}'.format(self.side, driver_b[0], 'tz'), bw_b.input[0])
        pm.connectAttr('{}{}.{}'.format(self.side, driver_b[1], 'tz'), bw_b.input[1])
        bw_b.weight[0].set(0.5)
        bw_b.weight[1].set(0.5)
        pm.connectAttr(bw_b.output, '{}{}.{}'.format(self.side, driven_b, 'tz'))
            
    # setup main BROW ctrl
    def set_brow_main(self):
        self.template.pop(-1)
        sel = [self.side + '_' + each for each in self.template]

        meshs = []
        for each in sel:
            ply = pm.polyPlane(axis=(0, 1, 0), sh=1, sw=1, h=0.1, w=0.1, ch=0)
            pm.matchTransform(ply, each)
            meshs.append(ply)

        driver_mesh = pm.polyUnite(meshs, ch=0, n=self.side+'_brow_rivet_surf')[0]

        pm.polyLayoutUV(self.side+'_brow_rivet_surf.f[*]', l=2, ch=0)

        cpom = pm.createNode('closestPointOnMesh')
        driver_mesh.worldMesh >> cpom.inMesh

        rivet_grp = 'brow_sys'
        if not pm.objExists(rivet_grp):
            pm.createNode('transform', n=rivet_grp)

        for item in sel:
            item = pm.PyNode(item)
            pos = pm.xform(item, q=1, t=1, ws=1)
            cpom.inPosition.set(pos)
            u = cpom.parameterU.get()
            v = cpom.parameterV.get()

            rivet = pm.createNode('follicle', n=item.name().replace('loc', 'rivetShape'))
            rivet_transform = pm.rename(rivet.parent(0), item.name().replace('loc', 'rivet'))
            pm.parent(rivet_transform, rivet_grp)

            driver_mesh.worldMesh >> rivet.inputMesh
            driver_mesh.worldMatrix[0] >> rivet.inputWorldMatrix

            rivet.parameterU.set(u)
            rivet.parameterV.set(v)

            folcle_tfm = rivet.getParent()
            rivet.outTranslate >> folcle_tfm.translate
            rivet.outRotate >> folcle_tfm.rotate

            self.parent_constraint_with_matrix(folcle_tfm, item.replace('_loc', '_ctrl'))

        pm.skinCluster('%s_brow_jnt' % self.side, driver_mesh, tsb=True, dr=8.0, n=self.side + '_browRivet_skin')
        brow_bind_pvt = self.brow_data.get(self.side+'_brow_ctrl').get_node('piv_pre')
        pm.connectAttr(brow_bind_pvt.parentInverseMatrix[0], self.side + '_browRivet_skin.bindPreMatrix[0]')
        pm.parent(driver_mesh, rivet_grp)
        pm.delete(cpom)

    def build_forehead(self):

        sel = [self.side + each for each in ['_foreHeadIn_loc', '_foreHeadSubIn_loc', '_foreHeadMid_loc',
                                             '_foreHeadSubOut_loc', '_foreHeadOut_loc']]

        if not sel:
            return
        for each in sel:
            each = pm.PyNode(each)

            ctrl_obj = control.Control(BROW.__name__, self.version, self.side, self.side + '_' + BROW.__name__)

            ctrl_obj.build(each)

            self.brow_data['ctrl'] = ctrl_obj

    def build_mid_brow(self):
        if pm.objExists('L_browIn_ctrl') and pm.objExists('R_browIn_ctrl'):
            tmp_loc = pm.createNode('locator')
            tmp_loc = pm.rename(tmp_loc.getParent(), 'M_brow_loc')
            pm.delete(pm.pointConstraint('L_browIn_ctrl', 'R_browIn_ctrl', 'M_brow_loc', mo=0))
            # create ctrl
            #name = tmp_loc.name().replace('_loc', '')
            item = tmp_loc.name().replace('_loc', '_ctrl')

            ctrl_obj = control.Control(BROW.__name__, self.version, self.side, self.side + '_' + BROW.__name__)

            ctrl_obj.hierarchy = ['zro', 'con', 'ort', 'mir', 'piv', 'riv', 'ato', 'drn', 'ofs', 'nul']

            ctrl_obj.build(tmp_loc)

            self.brow_data[item] = ctrl_obj

            pm.delete(tmp_loc)
            self.average_mid_brow()

    def average_mid_brow(self):
        '''M_brow_obj = self.brow_data.get('M_brow_ctrl')
        L_brow_obj = self.brow_data.get('L_browIn_ctrl')
        R_brow_obj = self.brow_data.get('R_browIn_ctrl')

        M_brow_ato = M_brow_obj.get_node('ato')
        M_brow_sdk = M_brow_obj.get_node('drn')

        L_brow_ctrl = L_brow_obj.get_node('ctrl')
        L_brow_ato = L_brow_obj.get_node('ato')

        R_brow_ctrl = R_brow_obj.get_node('ctrl')
        R_brow_ato = R_brow_obj.get_node('ato')'''
        M_brow_ato = pm.PyNode('M_brow_ctrl_ato')
        M_brow_sdk = pm.PyNode('M_brow_ctrl_drn')
        M_brow_riv = pm.PyNode('M_brow_ctrl_riv')

        L_brow_ctrl = pm.PyNode('L_browIn_ctrl')
        L_brow_ato = pm.PyNode('L_browIn_ctrl_ato')
        L_brow_riv = pm.PyNode('L_browIn_ctrl_riv')

        R_brow_ctrl = pm.PyNode('R_browIn_ctrl')
        R_brow_ato = pm.PyNode('R_browIn_ctrl_ato')
        R_brow_riv = pm.PyNode('R_browIn_ctrl_riv')

        sdk_average = pm.createNode('plusMinusAverage', n=M_brow_sdk.name()+'_pma')
        sdk_average.operation.set(3)
        L_brow_ctrl.translate >> sdk_average.input3D[0]
        R_brow_ctrl.translate >> sdk_average.input3D[1]

        # sdk_average.output3Dx >> M_brow_sdk.tx
        sdk_average.output3Dy >> M_brow_sdk.ty
        sdk_average.output3Dz >> M_brow_sdk.tz

        ato_blend = pm.createNode('blendWeighted', n=M_brow_ato.name()+'_bw')
        ato_blend.weight[0].set(0.5)
        ato_blend.weight[1].set(0.5)

        L_brow_ato.tz >> ato_blend.input[0]

        R_brow_ato.tz >> ato_blend.input[1]

        ato_blend.output >> M_brow_ato.tz

        riv_average = pm.createNode('plusMinusAverage', n=M_brow_riv.name() + '_pma')
        riv_average.operation.set(3)
        L_brow_riv.translate >> riv_average.input3D[0]
        R_brow_riv.translate >> riv_average.input3D[1]

        # sdk_average.output3Dx >> M_brow_sdk.tx
        riv_average.output3Dy >> M_brow_riv.ty
        riv_average.output3Dz >> M_brow_riv.tz

    # @staticmethod
    def parent_constraint_with_matrix(self, src, tgt):

        # rivet_node = pm.PyNode(each.name().replace('_ctrl', '_rivet'))
        rivet_node = src

        riv_node = self.brow_data[tgt].get_node('riv')

        con_node = self.brow_data[tgt].get_node('con')

        piv_node = self.brow_data[tgt].get_node('piv')

        offset = pm.createNode('multMatrix', n=riv_node.name()+'_ofs_mm')

        con_node.worldMatrix[0] >> offset.matrixIn[0]

        get_wm = pm.getAttr(rivet_node.worldInverseMatrix[0])

        pm.setAttr(offset.matrixIn[1], get_wm)

        mult = pm.createNode('multMatrix', n=riv_node.name()+'_mm')
        offset.matrixSum >> mult.matrixIn[0]
        rivet_node.worldMatrix[0] >> mult.matrixIn[1]
        piv_node.parentInverseMatrix[0] >> mult.matrixIn[2]

        dcom = pm.createNode('decomposeMatrix', n=riv_node.name()+'_dm')
        mult.matrixSum >> dcom.inputMatrix

        dcom.outputTranslate >> riv_node.translate
        dcom.outputRotate >> riv_node.rotate

    def fix_m_brow_tx(self):

        riv_node = self.brow_data['M_brow_ctrl'].get_node('riv')

        conection = riv_node.t.listConnections(d=1)[-1]
        pm.disconnectAttr(conection.outputTranslate, riv_node.translate)

        conection.outputTranslateY >> riv_node.ty
        conection.outputTranslateZ >> riv_node.tz

    def add_z_attr(self):
        for each in self.brow_data.keys():

            if each.endswith('_ctrl'):
                pm.addAttr(each, ln='Z', k=1)
                mdl = pm.createNode('multDoubleLinear', n=each+'Z_mdl')
                pm.connectAttr(each+'.Z',  mdl.input1)
                mdl.input2.set(0.1)
                pm.connectAttr(mdl.output, each+'.tz')
                pm.setAttr(each+'.tz', l=1, k=0)

    def setup_network(self):
        for key in self.brow_data.keys():
            net = network.Network(BROW.__name__)
            net.add_attr(key)
            net.set_connection(pm.PyNode(key), key)

    def get_bind(self):
        binds = []
        for key in self.brow_data.keys():
            if key.endswith('_ctrl'):
                inst = self.brow_data.get(key)
                binds.append(inst.get_node('bind'))
        return binds

    def set_hierarchy(self):
        pass