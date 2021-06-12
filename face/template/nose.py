from lib import template

from importlib import reload

reload(template)


class NoseTemplate(template.Template):
    def __init__(self):
        super(NoseTemplate, self).__init__()
        self._nose_template = {'M_nose_loc': {'pos': [0.0, 148.343, 12.942],
                                              'rot': [0.0, 0.0, 0.0]},
                               'M_noseTip_loc': {'pos': [0.0, 145.754, 15.167],
                                                 'rot': [0.0, 0.0, 0.0]},
                               'M_noseMid_loc': {'pos': [0.0, 146.52, 13.635],
                                                 'rot': [0.0, 0.0, 0.0]},
                               'M_noseBtm_loc': {'pos': [0.0, 145.024, 13.489],
                                                 'rot': [0.0, 0.0, 0.0]},
                               'L_nostril_loc': {'pos': [0.501, 145.476, 13.964],
                                                 'rot': [0.0, 0.0, 0.0]},
                               'R_nostril_loc': {'pos': [-0.501, 145.476, 13.964],
                                                 'rot': [0.0, 0.0, 0.0]}
                               }

    def nose(self):
        for name, data in self._nose_template.items():
            self.build('nose', name, data['pos'], data['rot'])
