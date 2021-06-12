from lib import template

from importlib import reload

reload(template)


class JawTemplate(template.Template):
    def __init__(self):
        super(JawTemplate, self).__init__()
        self._jaw_template = {'M_jawMain_loc': {'pos': [0.0, 147.118, 1.578],
                                                'rot': [0.0, 0.0, 0.0]},
                              'M_jawMid_loc': {'pos': [0.0, 142.996, 7.596],
                                               'rot': [0.0, 0.0, 0.0]},
                              'M_jawTip_loc': {'pos': [0.0, 140.771, 11.608],
                                               'rot': [0.0, 0.0, 0.0]},
                              'M_chin_loc': {'pos': [0.0, 140.005, 10.769],
                                             'rot': [0.0, 0.0, 0.0]},
                              }

    def jaw(self):
        for name, data in self._jaw_template.items():
            self.build('jaw', name, data['pos'], data['rot'])
