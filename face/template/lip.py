from lib import template

from importlib import reload

reload(template)


class LipTemplate(template.Template):
    def __init__(self):
        super(LipTemplate, self).__init__()
        self._lip_template = {'L_lipCorner_loc': {'pos': [2.899, 141.559, 12.085],
                                                  'rot': [0.0, 30.0, 0.0]},
                              'L_upLip1_loc': {'pos': [1.114, 142.491, 14.594],
                                               'rot': [0.0, 0.0, 0.0]},
                              'L_upLip2_loc': {'pos': [2.069, 142.104, 14.016],
                                               'rot': [17.242, 26.971, -10.067]},
                              'L_upLipMid_loc': {'pos': [1.617, 142.315, 14.343],
                                                 'rot': [0.0, 0.0, 0.0]},
                              'L_upLipEnd_loc': {'pos': [2.771, 141.702, 13.173],
                                                 'rot': [40.17, 27.67, 0.0]},
                              'M_upLip_loc': {'pos': [0.0, 142.658, 14.829],
                                              'rot': [0.0, 0.0, 0.0]},
                              'L_loLip1_loc': {'pos': [0.921, 141.057, 13.984],
                                               'rot': [0.0, 22.64, 0.0]},
                              'L_loLip2_loc': {'pos': [1.788, 141.175, 13.528],
                                               'rot': [0.0, 45.0, 0.0]},
                              'L_loLipMid_loc': {'pos': [1.366, 141.105, 13.796],
                                                 'rot': [0.0, 45.0, 0.0]},
                              'L_loLipEnd_loc': {'pos': [2.43, 141.369, 12.752],
                                                 'rot': [0.0, 45.0, 0.0]},
                              'M_upperLip_ctrl': {'pos': [0.0, 141.018, 14.131],
                                                  'rot': [0.0, 0.0, 0.0]},
                              'M_lowerLip_ctrl': {'pos': [0.0, 141.018, 14.131],
                                                  'rot': [0.0, 0.0, 0.0]},
                              'M_mouth_ctrl': {'pos': [0.0, 141.018, 14.131],
                                               'rot': [0.0, 0.0, 0.0]},
                              'M_upperLipPuff_ctrl': {'pos': [0.0, 141.018, 14.131],
                                                      'rot': [0.0, 0.0, 0.0]},
                              'M_lowerLipPuff_ctrl': {'pos': [0.0, 141.018, 14.131],
                                                      'rot': [0.0, 0.0, 0.0]}

                              }

    def lip(self):
        for name, data in self._lip_template.items():
            self.build('lip', name, data['pos'], data['rot'])
