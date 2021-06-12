from lib import template

from importlib import reload

reload(template)


class SkullTemplate(template.Template):
    def __init__(self):
        super(SkullTemplate, self).__init__()
        self._skull_template = {'M_scalp_ctrl': {'pos': [2.899, 141.559, 12.085],
                                                'rot': [0.0, 30.0, 0.0]},
                                'M_faceUpper_ctrl': {'pos': [1.114, 142.491, 14.594],
                                                    'rot': [0.0, 0.0, 0.0]},
                                'M_faceMid_ctrl': {'pos': [2.069, 142.104, 14.016],
                                                  'rot': [17.242, 26.971, -10.067]},
                                'M_mappet_ctrl': {'pos': [1.617, 142.315, 14.343],
                                                'rot': [0.0, 0.0, 0.0]},
                                'M_faceLower_ctrl': {'pos': [2.771, 141.702, 13.173],
                                                      'rot': [40.17, 27.67, 0.0]}

                                }

    def cheek(self):
        for name, data in self._skull_template.items():
            self.build('cheek', name, data['pos'], data['rot'])
