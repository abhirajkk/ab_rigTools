from lib import control
from importlib import reload

reload(control)

from utils import utility

reload(utility)

VERSION = "0.1"


class EAR:
    def __init__(self):
        self.ear_data = {}

    def rig(self):
        ear_template = utility.get_template_from_tag('EarTemplate')
        if ear_template is None:
            return "No valid ear template found !!"

        for item in ear_template:
            control_inst = control.Control(self.__class__.__name__, VERSION, item.split('_')[0],
                                           '{}_{}'.format(item.split('_')[0], self.__class__.__name__))
            control_inst.build(item)
            self.ear_data[control_inst.data['ctrl']] = control_inst.data

        print (self.ear_data.items())