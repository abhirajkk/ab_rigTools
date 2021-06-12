from importlib  import reload
from face.template import brow
reload(brow)
from face.template import cheek
reload(cheek)
from face.template import ear
reload(ear)
from face.template import eye
reload(eye)
from face.template import jaw
reload(jaw)
from face.template import lip
reload(lip)


class Generic:
    def __init__(self):
        brow_inst = brow.BrowTemplate()
        brow_inst.brow()

        eye_inst = eye.EyeTemplate()
        eye_inst.eye()

        lip_inst = lip.LipTemplate()
        lip_inst.lip()

        ear_inst = ear.EarTemplate()
        ear_inst.ear()

        jaw_inst = jaw.JawTemplate()
        jaw_inst.jaw()

        cheek_inst = cheek.CheekTemplate()
        cheek_inst.cheek()
