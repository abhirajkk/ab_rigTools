from lib import template

from importlib import reload

reload(template)


class EarTemplate(template.Template):
    def __init__(self):
        super(EarTemplate, self).__init__()
        self._ear_template = {'L_ear_loc': {'pos': [9.733, 147.821, -0.407],
                                            'rot': [0.0, 0.0, 0.0]},
                              'L_earTop_loc': {'pos': [11.697, 150.819, -3.146],
                                               'rot': [0.0, 0.0, 0.0]},
                              'L_earMid_loc': {'pos': [12.22, 147.139, -3.699],
                                               'rot': [0.0, 0.0, 0.0]},
                              'L_earBtm_loc': {'pos': [9.665, 144.501, -0.698],
                                               'rot': [0.0, 0.0, 0.0]},
                              'R_ear_loc': {'pos': [-9.733, 147.821, -0.407],
                                            'rot': [0.0, 0.0, 0.0]},
                              'R_earTop_loc': {'pos': [-11.697, 150.819, -3.146],
                                               'rot': [0.0, 0.0, 0.0]},
                              'R_earMid_loc': {'pos': [-12.22, 147.139, -3.699],
                                               'rot': [0.0, 0.0, 0.0]},
                              'R_earBtm_loc': {'pos': [-9.665, 144.501, -0.698],
                                               'rot': [0.0, 0.0, 0.0]}
                              }

    def ear(self):
        for name, data in self._ear_template.items():
            self.build('ear', name, data['pos'], data['rot'])
