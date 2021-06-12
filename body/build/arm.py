import body.modules.limbIk
reload(body.modules.limbIk)


def test():
    # version, side, name, start_jnt, mid_jnt, end_jnt)
    inst = body.modules.limbIk.LimbIk('0.1', 'L', 'arm', 'joint1', 'joint2', 'joint3')
    inst.build()
