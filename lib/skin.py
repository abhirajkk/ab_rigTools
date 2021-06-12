import pymel.core as pm


def add_skin_cluster(geo, jnts):
    pass


def combine_skin_cluster(skins):
    pass


def separate_skin_cluster(skins):
    pass


def connect_pre_matrix(skin, detach=False):
    jnts = pm.skinCluster(skin, q=1, inf=1)
    for i, each in enumerate(jnts):
        node = pm.PyNode(each.replace('_jnt', '_pre_piv'))
        pm.connectAttr(node + '.parentInverseMatrix[0]', '%s.bindPreMatrix[%d]' % (skin, i))

        if detach:
            pre_node = pm.PyNode(each.replace('_bind', '_pre_con'))
            node = pm.PyNode(each.replace('_bind', '_con'))
            pm.disconnectAttr(node.translate, pre_node.translate)
            pm.disconnectAttr(node.rotate, pre_node.rotate)
            pm.disconnectAttr(node.scale, pre_node.scale)


def get_weights_from_transform(skin, obj, transform):
    weights = {}
    vertices = pm.polyEvaluate(obj, vertex=True)
    for i in range(vertices):
        wt = pm.skinPercent(skin, '%s.vtx[%d]' % (obj, i), q=1, transform=transform)
        weights['%s.vtx[%d]' % (obj, i)] = wt
    return weights


def smooth_vertex_weights(skin, jnt, base_jnt, rev=False):
    sel = pm.ls(os=1)
    if not sel:
        print "please select vert"
        return
    if rev:
        sel.reverse()

    for i, each in enumerate(sel):
        count = len(sel)
        wt = i * 1.0 / (count - 1.0)
        pm.skinPercent(skin, each, tv=(jnt, wt))
        pm.skinPercent(skin, each, tv=(base_jnt, (1 - wt)))



src = ['L_lidIn_ctrl', 'L_upLid_1_ctrl', 'L_upLid_2_ctrl', 'L_upLid_3_ctrl', 'L_lidOut_ctrl']

base_crv = pm.PyNode('curve_baseShape')
orig_cvs = base_crv.getCVs(space="world")

tgt_crv = pm.PyNode('curveShape1')

result = {}
for each in src:
    node = pm.PyNode(each)
    node.translateY.set(1)
    current_cvs = tgt_crv.getCVs(space="world")

    wt_lst = get_cv_weights(orig_cvs, current_cvs)
    result[each] = wt_lst
    node.translateY.set(0)


def get_cv_weights(src, tgt):
    weights = {}
    for i, each in enumerate(src):
        wt = (tgt[i] - src[i]).length()
        weights[i] = wt
    return weights


def set_weights(curve, skin, weigths_dict):
    for key in weigths_dict.keys():
        item = weigths_dict[key]
        for cvs in item.keys():
            pm.skinPercent(skin, '{}.{}'.format(curve, 'cv[%d]' % cvs),
                           tv=(key.replace('_ctrl', '_drv_jnt'), item[cvs]))


set_weights('curve1', 'skinCluster10', result)

def get_vert_weight(skin):
    """
    need select single vetex
    """
    sel = pm.ls(sl=1, fl=1)[0]
    
    weights = {}
    head_wt = pm.skinPercent(skin,each,q=1,t='head_bind')
    jaw_wt = pm.skinPercent(skin,each,q=1,t='jaw_bind')
    weights['head_bind'] = head_wt
    weights['jaw_bind'] = jaw_wt
    return weights
        
# set 
def set_weight_to_vertices(skin, weight):
    """
    need to select multiple vertices 
    """
    sel = pm.ls(sl=1, fl=1)
    infs = weight.keys()
    for i,each in enumerate(sel):
        head, jaw = weight[infs[0]],  weight[infs[1]]
        head_wt = pm.skinPercent(skin,each,tv=('head_bind', head))
        jaw_wt = pm.skinPercent(skin,each, tv=('jaw_bind', jaw))