import pymel.core as pm

from ab_rigTools.Lib import controls
reload(controls)


class LimbIk:
    def __init__(self, version, side, name, start_jnt, mid_jnt, end_jnt):
        self.side = side
        self.name = name
        self.version = version
        self.start_jnt = start_jnt
        self.mid_jnt = mid_jnt
        self.end_jnt = end_jnt
        self.data = {}
        self.ik_chain = []
        self.ik_ctrl = None

        if pm.objExists('{}_{}_{}'.format(self.side, self.name, 'grp')):
            self.ik_main_grp = '{}_{}_{}'.format(self.side, self.name, 'grp')
        else:
            self.ik_main_grp = pm.createNode('transform', n='{}_{}_{}'.format(self.side, self.name, 'grp'))

    def build(self):
        self.build_ik_chain()
        self.build_ik()

    def build_ik_chain(self):
        root = pm.duplicate(self.start_jnt, rc=1)[0]
        ik_jnts = pm.listRelatives(root, ad=True)
        ik_jnts.reverse()
        ik_jnts.insert(0, root)
        for i in range(len(ik_jnts)):
            name_pref = ik_jnts[i].split('_CJ')
            self.ik_chain.append(pm.rename(ik_jnts[i], (name_pref[0] + "_IK")))

    def build_ik(self):
        ik_h = pm.ikHandle(sj=self.ik_chain[0], ee=self.ik_chain[2], sol='ikRPsolver',
                           n='{}_{}_{}'.format(self.side, self.name, 'ikH'))[0]
        ik_h.visibility.set(0)

        ik_ctrl = controls.CtrlCurve(name='{}_{}_{}'.format(self.side, self.name+'Ik', 'ctrl'), scale=1)
        self.ik_ctrl = ik_ctrl.trans
        ik_ctrl.box()
        ik_ctrl.rotorder()
        ik_ctrl_grp = ik_ctrl.grpTrans()
        pm.matchTransform(ik_ctrl_grp, self.ik_chain[-1], pos=True, rot=False)
        pm.parent(ik_h, self.ik_ctrl)

        controls.ColorShape([self.ik_ctrl], 'blue')
        pm.addAttr(self.ik_ctrl, ln="stretch", min=0, max=1, k=1)
        pm.addAttr(self.ik_ctrl, ln="soft", min=0, max=1, k=1)
        pm.addAttr(self.ik_ctrl, ln="elbowLock", min=0, max=1, k=1)
        pm.addAttr(self.ik_ctrl, ln="elbowSlide", min=-1, max=1, k=1)

        top_grp = pm.createNode('transform', n=self.ik_chain[0].name()+'_grp')
        pm.matchTransform(top_grp, self.ik_chain[0])
        mid_grp = pm.createNode('transform', n=self.ik_chain[1].name() + '_grp')
        pm.matchTransform(mid_grp, self.ik_chain[1])

        #end_grp = pm.createNode('transform', n=self.ik_chain[2].name() + '_grp')
        #pm.matchTransform(end_grp, self.ik_chain[2])

        stretch_node = pm.createNode('stretchIkNode', n='{}_{}_{}'.format(self.side, self.name, 'ikStretch'))
        stretch_node.upperLength.set(self.ik_chain[1].tx.get())
        stretch_node.lowerLength.set(self.ik_chain[2].tx.get())

        top_grp.worldMatrix[0] >> stretch_node.start
        mid_grp.worldMatrix[0] >> stretch_node.poleVector
        ik_node = pm.PyNode(self.ik_ctrl)
        ik_node.worldMatrix[0] >> stretch_node.end

        stretch_node.outUpper >> self.ik_chain[1].tx
        stretch_node.outLower >> self.ik_chain[2].tx

        ik_node.stretch >> stretch_node.stretch
        ik_node.soft >> stretch_node.soft
        ik_node.elbowLock >> stretch_node.elbowLock
        ik_node.elbowSlide >> stretch_node.slide

        # clean up
        pm.parent(self.ik_chain[0],  ik_ctrl_grp, top_grp, mid_grp, self.ik_main_grp)

    def set_pole_vec(self):
        pass