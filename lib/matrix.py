import pymel.core as pm


def offset_parent_constraint(src, tgt, blend=False, w=0.5):
    src_node = pm.PyNode(src)
    tgt_node = pm.PyNode(tgt)
    tgt_piv_node = pm.PyNode(tgt_node.name().replace('ato', 'piv'))

    offset_matrix = pm.createNode('multMatrix', n=tgt_node.name()+'_offset_mat')
    tgt_piv_node.worldMatrix[0] >> offset_matrix.matrixIn[0]
    src_node.parentInverseMatrix[0] >> offset_matrix.matrixIn[1]

    mult_matrix = pm.createNode('multMatrix', n=tgt_node.name() + '_mat')
    offset_matrix.matrixSum >> mult_matrix.matrixIn[0]
    src_node.worldMatrix[0] >> mult_matrix.matrixIn[1]
    tgt_node.parentInverseMatrix[0] >> mult_matrix.matrixIn[2]

    decomp = pm.createNode('decomposeMatrix', n=tgt_node.name() + '_dcom')

    mult_matrix.matrixSum >> decomp.inputMatrix

    if blend:
        blend_node = pm.createNode('pairBlend', n=tgt_node.name()+'_pb')
        blend_node.weight.set(w)
        decomp.outputTranslate >> blend_node.inTranslate1
        decomp.outputRotate >> blend_node.inRotate1

        blend_node.outTranslate >> tgt_node.translate
        blend_node.outRotate >> tgt_node.rotate

    else:
        decomp.outTranslate >> tgt_node.translate
        decomp.outRotate >> tgt_node.rotate
