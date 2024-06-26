from lib import template

from importlib import reload

reload(template)


class BrowTemplate(template.Template):
    def __init__(self):
        super(BrowTemplate, self).__init__()
        self._brow_template = {'L_browIn_loc': {'pos': [2.983729839324951, 153.50050354003906, 13.941984176635742],
                                                'rot': [0.0, 0.0, 0.0]},
                               'L_browSubIn_loc': {'pos': [4.435447692871094, 153.89979553222656, 13.495194435119629],
                                                   'rot': [0.0, 0.0, 0.0]},
                               'L_browMid_loc': {'pos': [5.997332572937012, 154.28150939941406, 12.712636947631836],
                                                 'rot': [0.0, 0.0, 0.0]},
                               'L_browSubOut_loc': {'pos': [7.269223690032959, 154.4889373779297, 11.633390426635742],
                                                    'rot': [0.0, 0.0, 0.0]},
                               'L_browOut_loc': {'pos': [8.365519523620605, 154.2812042236328, 10.221451759338379],
                                                 'rot': [0.0, 0.0, 0.0]},
                               'M_brow_loc': {'pos': [0.0, 153.3841094970703, 14.318720817565918],
                                              'rot': [0.0, 0.0, 0.0]},
                               'R_browIn_loc': {'pos': [-2.983729839324951, 153.50050354003906, 13.941984176635742],
                                                'rot': [0.0, 0.0, 0.0]},
                               'R_browSubIn_loc': {'pos': [-4.435447692871094, 153.89979553222656, 13.495194435119629],
                                                   'rot': [0.0, 0.0, 0.0]},
                               'R_browMid_loc': {'pos': [-5.997332572937012, 154.28150939941406, 12.712636947631836],
                                                 'rot': [0.0, 0.0, 0.0]},
                               'R_browSubOut_loc': {'pos': [-7.269223690032959, 154.4889373779297, 11.633390426635742],
                                                    'rot': [0.0, 0.0, 0.0]},
                               'R_browOut_loc': {'pos': [-8.365519523620605, 154.2812042236328, 10.221451759338379],
                                                 'rot': [0.0, 0.0, 0.0]}}

    def brow(self):
        for name, data in self._brow_template.items():
            self.build('brow', name, data['pos'], data['rot'])
